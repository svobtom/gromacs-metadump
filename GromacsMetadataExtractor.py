"""
Description: This script extracts metadata from Gromacs TPR files acording to the schema
Author: Adrian Rosinec, and Ondrej Sindler
Maintainer: Adrian Rosinec
Email: adrian@ics.muni.cz
Date Created: February 13, 2023
Date Modified: January 1, 2024
Dependencies: Python 3.8+, Gromacs 2020.4+
Version: 0.1
Python Version: 3.8+
License: BSD 3-Clause License

Usage:

    from GromacsMetadataExtractor import MetadataExtractor

    extractor_object = MetadataExtractor(tpr_file[, gro_file[, cpt_file[, debug]]])
    metadata = extractor_object.run().export()
    # Print `metadata` dictionary
    print(metadata)

"""

import datetime
import json
import os
import re
import subprocess

"""
Metadata extractor class for Gromacs tpr files.
Usage:
    MetadataExtractor(tpr_file[, gro_file[, cpt_file[, debug]]]) -> MetadataExtractor
params:
    tpr_file: path to the tpr file (required)
    gro_file: path to the gro file
    cpt_file: path to the cpt file
    debug: if true, debug information is printed as script runs
"""

class MetadataExtractor():

    tpr_file = None
    gro_file = None
    cpt_file = None

    tpr_lines = []
    tpr_lines_err = []
    main_information = {}
    detailed_information = {}
    tcoupl = None
    pcoupl = None
    metadata = {}
    debug = True

    error_code = 0

    tpx_version = None
    dump_sw_version = None

    def __init__(self, tpr, gro, cpt, debug):
        self.tpr_file = tpr
        self.gro_file = gro
        self.cpt_file = cpt
        self.debug = debug
        
        if not os.path.isfile(self.tpr_file):
            exit(f"\nERROR! There is no file {self.tpr_file}!\n")

    def load_tpr_lines(self) -> list:
        """
        Loads the whole gmx dump to the data structure
        """
        try:
            r = subprocess.run(f"gmx dump -s {self.tpr_file}", shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            self.error_code = r.returncode
            self.tpr_lines = [line.split() for line in r.stdout.lower().splitlines()]
            self.tpr_lines_err = r.stderr

            if self.debug and r.stderr:
                print("Error: ", r.stderr)

        except BaseException as e:
            print("Error: ", e)
            self.error_code = 1

        return self.tpr_lines

    def load_file_and_sw_versions(self):
        if not self.tpr_lines_err:
            self.load_tpr_err_lines()

        try:
            m = re.search(r'file tpx.* ([0-9]+), software.* ([0-9]+)', self.tpr_lines_err)
            self.tpx_version = m.group(1)
            self.dump_sw_version = m.group(2)
        except:
            self.tpx_version = "N/A"
            self.dump_sw_version = "N/A"

    def extract_main_information(self) -> dict:
        def _list_of_molecules():
            shortcuts = {'ala': 'A',
                        'arg': 'R',
                        'asn': 'N',
                        'asp': 'D',
                        'asx': 'B',
                        'cys': 'C',
                        'glu': 'E',
                        'gln': 'Q',
                        'glx': 'Z',
                        'gly': 'G',
                        'his': 'H',
                        'ile': 'I',
                        'leu': 'L',
                        'lys': 'K',
                        'met': 'M',
                        'phe': 'F',
                        'pro': 'P',
                        'ser': 'S',
                        'thr': 'T',
                        'trp': 'W',
                        'tyr': 'Y',
                        'val': 'V',
                        'hsd': 'H (HSD)'}
            mols_data = {}
            mcounter = 0
            for i, sl in enumerate(self.tpr_lines):
                if sl == ["molblock", f"({mcounter}):"]:
                    mcounter += 1
                    mname = self.tpr_lines[i + 1][-1][1:-1]
                    nmols = self.tpr_lines[i + 2][-1]
                    mols_data[f"molecule {mcounter}"] = {"name": mname,
                                                        "count": int(nmols)}
            for x in range(mcounter):
                for index, sl in enumerate(self.tpr_lines):
                    if bool(re.search("moltype \((\d+)\):", " ".join(sl))) and self.tpr_lines[index + 1] == [f"name=\"{mols_data[f'molecule {x + 1}']['name']}\""]:
                        while not bool(re.search("residue \((\d+)\)", " ".join(self.tpr_lines[index]))):
                            index += 1
                        index += 1
                        residues = []
                        while self.tpr_lines[index][0][:7] == "residue":
                            residues.append("".join(self.tpr_lines[index]).split("=")[2][1:-4])
                            index += 1
                        # if len(list(set(shortcuts.keys()).intersection(set(residues)))):
                        mols_data[f"molecule {x + 1}"]["residues"] = [shortcuts.get(res.lower(), res) for res in residues]


            out_mols_data = []
            for key, value in mols_data.items():
                out_mols_data.append(dict({"id": key}, **value))

            self.main_information["molecules"] = out_mols_data

        self.main_information = {"force_field": "probably has to be set by the user"}

        # r = subprocess.check_output(f"gmx dump -s {self.tpr_file} 2> /dev/null", shell=True, text=True)

        if self.gro_file:
            self.main_information["box_size_and_shape"] = [float(n) for n in
                                                                    open(self.gro_file, "r").readlines()[
                                                                        -1].rstrip().split()]

        integrator = self.get_value_for_key("integrator")
        if integrator in ["steep", "cg"]:
            self.main_information["simulation_type"] = "energy minimization"
        elif integrator == "sd" or integrator[:2] == "md":
            self.main_information["simulation_type"] = "molecular dynamics"
            self.main_information["simulation_time_step"] = self.get_value_for_key("dt")
            if self.cpt_file is None:
                self.main_information["simulation_length"] = self.main_information[
                                                                "simulation_time_step"] * self.get_value_for_key("nsteps")
            else:
                pass
                cmd = f"gmx check -f {self.cpt_file} 2>&1 | grep \"Last frame\""
                r = subprocess.check_output(cmd, shell=True, text=True)
                self.main_information["simulation_length"] = float(r.splitlines()[1].split()[4])
        self.tcoupl = self.get_value_for_key("tcoupl")
        self.pcoupl = self.get_value_for_key("pcoupl")
        if self.tcoupl == self.pcoupl == "no":
            self.main_information["statistical_ensamble"] = "NVE (microcanonical)"
        elif self.tcoupl in ["nose-hoover", "v-rescale", "berendsen", "andersen", "andersen-massive"] and self.pcoupl == "no":
            self.main_information["statistical_ensamble"] = "NVT (canonical)"
            self.main_information["reference_temperature"] = self.find_all_values_for_key("ref-t")
        elif self.tcoupl in ["nose-hoover", "v-rescale", "berendsen", "andersen", "andersen-massive"] and self.pcoupl in ["berendsen", "parrinello-rahman"]:
            self.main_information["statistical_ensamble"] = "NpT (isothermal-isobaric)"
            self.main_information["reference_temperature"] = self.find_all_values_for_key("ref-t")
            self.main_information["reference_pressure"] = self.find_matrix_with_key("ref-p")
        _list_of_molecules()
        self.store_values_for_keys(target=self.main_information,
                            keys=(("free_energy_calculation", "free-energy"),
                                    ("umbrella_sampling", "pull"),
                                    ("AWH_adaptive_biasing", "awh")))


    def extract_detailed_information(self) -> dict:
        def _find_tc_grps():
            for sl in self.tpr_lines:
                if sl and sl[0] == "grp[t-coupling":
                    nr = int(sl[2][3:-1])
                    name = " ".join(sl[4:])[:-1]
                    self.detailed_information["thermostat"]["tc-grps"] = {"nr": nr, "name": name}
                    break
            else:
                if self.debug: print("Warning, no value for tc-grps founded!")

        if self.main_information["simulation_type"] == "energy minimization":
            self.store_values_for_keys(target=self.detailed_information,
                                keys=("emtol",
                                        "emstep"))
        if self.tcoupl != "no":
            self.store_values_for_keys(target=self.detailed_information,
                                keys=("tcoupl",
                                        "nsttcouple"),
                                group="thermostat")
            self.detailed_information["thermostat"]["tau-t"] = self.find_all_values_for_key("tau-t")
            _find_tc_grps()
        if self.pcoupl != "no":
            self.store_values_for_keys(target=self.detailed_information,
                                keys=("pcoupl",
                                        "refcoord-scaling",
                                        "pcoupltype",
                                        "tau-p"),
                                group="barostat")
            self.detailed_information["barostat"]["compressibility"] = self.find_matrix_with_key("compressibility")
        self.store_values_for_keys(target=self.detailed_information,
                            keys=("rvdw",
                                    "vdw-type",
                                    "rvdw-switch",
                                    "vdw-modifier",
                                    "dispcorr"),
                            group="van_der_Waals_interactions")
        self.store_values_for_keys(target=self.detailed_information,
                            keys=("coulombtype",
                                    "coulomb-modifier",
                                    "rcoulomb",
                                    "epsilon-r",
                                    "epsilon-rf"),
                            group="electrostatic_interactions")
        self.store_values_for_keys(target=self.detailed_information,
                            keys=("cutoff-scheme",
                                    "nstlist",
                                    "pbc",
                                    "rlist"),
                            group="neighbour_list")

        self.store_values_for_keys(target=self.detailed_information,
                            keys=("constraint-algorithm",
                                    "constraints",
                                    "lincs-order",
                                    "lincs-iter",
                                    "comm-grps",
                                    "nstcomm",
                                    "comm-mode"))
        if self.detailed_information["electrostatic_interactions"]["coulombtype"] == "pme":
            self.store_values_for_keys(target=self.detailed_information,
                                keys=("fourierspacing",))
        if self.main_information["free_energy_calculation"] == "yes":
            self.store_values_for_keys(target=self.detailed_information,
                                keys=("init-lambda",
                                        "delta-lambda",
                                        "sc-alpha",
                                        "sc-power",
                                        "sc-sigma"))


    def add_umbrella_sampling_information(self):
        def _find_dim(index: int,
                    i: int):
            for index, sl in enumerate(self.tpr_lines[index:], start=index):
                if bool(re.search("dim \((\d+)\):", " ".join(sl))):
                    dim = []
                    for n in range(1, int(sl[1][1:-2]) + 1):
                        dim.append(self.convert_str_to_int_float_bool("".join(self.tpr_lines[index + n]).split("=")[1]))
                    break
            self.detailed_information["umbrella_sampling"][f"pull-coord{i}-dim"] = dim

        def _find_vec(index: int,
                    i: int):
            for index, sl in enumerate(self.tpr_lines[index:], start=index):
                if bool(re.search("vec \((\d+)\):", " ".join(sl))):
                    vec = []
                    for n in range(1, int(sl[1][1:-2]) + 1):
                        vec.append(self.convert_str_to_int_float_bool("".join(self.tpr_lines[index + n]).split("=")[1]))
                    break
            self.detailed_information["umbrella_sampling"][f"pull-coord{i}-vec"] = vec

        def _find_groups(index: int,
                        i: int):
            while not bool(re.search("group\[(\d+)\]", self.tpr_lines[index][0])):
                index += 1
            groups = []
            while bool(re.search("group\[(\d+)\]", self.tpr_lines[index][0])):
                groups.append(self.convert_str_to_int_float_bool(self.tpr_lines[index][2]))
                index += 1
            self.detailed_information["umbrella_sampling"][f"pull-coord{i}-groups"] = groups

        self.detailed_information["umbrella_sampling"] = {}
        self.store_values_for_keys(target=self.detailed_information["umbrella_sampling"],
                            keys=("pull-ncoords",
                                    "pull-ngroups"))
        for i in range(self.detailed_information["umbrella_sampling"]["pull-ncoords"]):
            for index, sl in enumerate(self.tpr_lines):
                if sl == ["pull-coord", f"{i}:"]:
                    _find_dim(index, i)
                    _find_vec(index, i)
                    _find_groups(index, i)

                    self.store_first_values_for_keys_after_index(target=self.detailed_information,
                                                            names_keys=((f"pull-coord{i}-start", "start"),
                                                                        (f"pull-coord{i}-init", "init")),
                                                            index=index)
                    self.store_first_values_for_keys_after_index(target=self.detailed_information["umbrella_sampling"],
                                                            names_keys=((f"pull-coord{i}-type", "type"),
                                                                        (f"pull-coord{i}-geometry", "geometry"),
                                                                        (f"pull-coord{i}-rate", "rate"),
                                                                        (f"pull-coord{i}-k", "k")),
                                                            index=index)
                    if self.detailed_information["umbrella_sampling"][f"pull-coord0-geometry"] == "cylinder":
                        self.store_values_for_keys(target=self.detailed_information["umbrella_sampling"],
                                            keys=("pull-cylinder-r",))


    def add_awh_information(self):
        self.detailed_information["AWH_adaptive_biasing"] = {}
        self.store_values_for_keys(target=self.detailed_information["AWH_adaptive_biasing"],
                            keys=("awh-nbias",))
        self.store_values_for_keys(target=self.detailed_information,
                            keys=("awh-potential",
                                    "awh-share-bias-multisim"))
        for awh_i in range(1, self.detailed_information["AWH_adaptive_biasing"]["awh-nbias"] + 1):
            self.store_values_for_keys(target=self.detailed_information["AWH_adaptive_biasing"],
                                keys=(f"awh{awh_i}-ndim",
                                        f"awh{awh_i}-error-init"))
            self.store_values_for_keys(target=self.detailed_information,
                                keys=(f"awh{awh_i}-target",
                                        f"awh{awh_i}-growth",
                                        f"awh{awh_i}-equilibrate-histogram"))

            for dim_i in range(1, self.detailed_information["AWH_adaptive_biasing"][f"awh{awh_i}-ndim"] + 1):
                for index, sl in enumerate(self.tpr_lines):
                    if sl == [f"awh{awh_i}-dim{dim_i}:"]:
                        self.store_first_values_for_keys_after_index(target=self.detailed_information["AWH_adaptive_biasing"],
                                                                names_keys=((f"awh{awh_i}-dim{dim_i}-cover-diameter", "cover-diameter"),
                                                                            (f"awh{awh_i}-dim{dim_i}-diffusion", "diffusion"),
                                                                            (f"awh{awh_i}-dim{dim_i}-coord-index", "coord-index"),
                                                                            (f"awh{awh_i}-dim{dim_i}-start", "start"),
                                                                            (f"awh{awh_i}-dim{dim_i}-end", "end"),
                                                                            (f"awh{awh_i}-dim{dim_i}-force-constant", "force-constant")),
                                                                index=index)


    def convert_str_to_int_float_bool(self, value):
        if value in ["true", "false"]:
            return value == "true"

        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass
        return value


    def get_value_for_key(self, key: str):
        filtered = [sl for sl in self.tpr_lines if [key, "="] == sl[:2] and len(sl) == 3]
        if len(filtered) > 1:
            if self.debug: print(f"Warning! More lines with keyword {key}!")
            return False
        elif len(filtered) == 0:
            if self.debug: print(f"Warning! No value for keyword {key}!")
            return False
        else:
            value = filtered[0][2]
            converted_value = self.convert_str_to_int_float_bool(value)
            return converted_value


    def store_values_for_keys(self, target: dict,
                            keys: tuple,
                            group: str = None):
        """If the key is a string, the value is stored under the same name as in the tpr file.
        If the key is tuple, the first element is used as the name to store in the metadata
        and the value in the tpr file is looked up by the second element."""
        if group:
            target[group] = {}
            target = target[group]
        for key in keys:
            if isinstance(key, str):
                name = key
            elif isinstance(key, tuple):
                name = key[0]
                key = key[1]
            filtered = [sl for sl in self.tpr_lines if [key, "="] == sl[:2] and len(sl) == 3]
            if len(filtered) > 1:
                if self.debug: print(f"Warning! More lines with keyword {key}!")
            elif len(filtered) == 0:
                if self.debug: print(f"Warning! No value for keyword {key}!")
            else:
                value = filtered[0][2]
                converted_value = self.convert_str_to_int_float_bool(value)
                target[name] = converted_value


    def store_first_values_for_keys_after_index(self, target: dict,
                                                names_keys: tuple,
                                                index: int):
        for name, key in names_keys:
            for sl in self.tpr_lines[index:]:
                if sl[0] == key:
                    target[name] = self.convert_str_to_int_float_bool(sl[2])
                    break
            else:
                if self.debug: print(f"Warning! No value for keyword {key}!")


    def find_all_values_for_key(self, key: str) -> list:
        for sl in self.tpr_lines:
            if sl[0] == f"{key}:":
                return [self.convert_str_to_int_float_bool(value) for value in sl[1:]]
        if self.debug: print(f"Warning! No values for keyword {key}")


    def find_matrix_with_key(self, key: str) -> list:
        filtered = [sl for sl in self.tpr_lines if sl and sl[0][:len(key)] == key]
        if len(filtered) != 4:
            exit(f"Wrong number of lines for keyword {key}")
        matrix = [[], [], []]
        for line_count in range(1, 4):
            for index in range(2, 5):
                matrix[line_count - 1].append(float(filtered[line_count][index].replace("}", "").replace(",", "")))
        return matrix


    def add_additional_info(self):
        self.metadata["_metadump_version"] = "1.0.0"
        self.metadata["_metadata_date"] = datetime.datetime.now().isoformat()
        self.metadata["_tpx_version"] = self.tpx_version
        self.metadata["_dump_sw_version"] = self.dump_sw_version
        self.metadata["_exit_code"] = self.error_code

        try:
            self.metadata["_gromacs_version"] = re.search("VERSION ([\d\.]+)", self.tpr_lines_err).group(1)
        except IndexError:
            self.metadata["_gromacs_version"] = "unknown"

    def keys_dash_to_underscore(self, data_old: dict):
        """Converts keys with dashes to keys with underscores."""
        data_new = {}

        for key, item in data_old.items():
            if isinstance(item, dict):
                item = self.keys_dash_to_underscore(item)

            data_new[key.replace("-", "_")] = item

        return data_new

    def run(self):
        """
        Runs the whole process of extracting metadata from the tpr file.
        """

        self.tpr_lines = self.load_tpr_lines()
        if self.tpr_lines:
            self.extract_main_information()
            self.extract_detailed_information()

            if self.main_information["umbrella_sampling"]:
                self.add_umbrella_sampling_information()

            if self.main_information["AWH_adaptive_biasing"]:
                self.add_awh_information()

            self.metadata = {"main_information": self.main_information,
                        "detailed_information": self.detailed_information}

        self.load_file_and_sw_versions()
        self.add_additional_info()
        # keys need to be renamed because repository doesn't support dashes
        self.metadata = self.keys_dash_to_underscore(self.metadata)

        return self

    def print(self, format="json"):
        """
        Prints the extracted metadata in json or yaml format.
        param format: json or yaml
        """

        if format == 'json':
            return json.dumps(self.metadata)
        elif format == 'yaml':
            import yaml
            return yaml.dump(self.metadata,
                            default_flow_style=False,
                            indent=4,
                            allow_unicode=True)

    def export(self):
        return self.metadata


if __name__ == "__main__":
    pass
