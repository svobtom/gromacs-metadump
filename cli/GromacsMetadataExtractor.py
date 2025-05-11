import os
from typing import MutableMapping
import json
import subprocess
import yaml
import re
import tarfile, zipfile, os
import tempfile

METADATA_STRUCTURE = {
    "simulation": {},
    "system": {},
    "administrative": {},
    "simulated_object": {},
}

class GromacsMetadataExtractor:
    def __init__(self, format="json", verbose=False, gmx_bin="/opt/gromacs/bin/gmx", **kwargs):
        self.format = format
        self.verbose = verbose
        self.metadata = METADATA_STRUCTURE
        self.gmx_bin = gmx_bin
        self.gmx_dump_options = None
        if kwargs:
            for key, value in kwargs.items():
                self.gmx_dump_options[key] = value
        else:
            self.gmx_dump_options = {
                "inputrec": True,
                "qm-opts": True,
                "grpopts": True,
                "header": True,
                "box": True,
                "box_rel": True,
                "boxv": True,
                "pres_prev": True,
                "svir_prev": True,
                "fvir_prev": True,
                "nosehoover_xi": True,
                "group_statistics": True
            }

    ALLOWED_EXTENSIONS = {"tpr", "gro", "top", "json", "yaml", "yml", "zip", "tar", "gz", "bz2", "custom-metadata"}

    def _allowed_file(self, filename):
        """Check if the file has an allowed extension."""
        return "." in filename and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def _merge_json(self, *json_data):
        """Merge multiple JSON objects into one."""
        merged = {}
        for data in json_data:
            if isinstance(data, dict):
                merged.update(data)
        return merged
    
    def merge_json2(self, target, source):
        """
        Recursively merge source into target.
        If a key exists in both target and source, the value from source is used.
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], MutableMapping) and isinstance(value, MutableMapping):
                self._merge_json(target[key], value)
            else:
                target[key] = value
    
    def _put_metadata(self, key, value):
        """Store metadata in the appropriate structure."""
        keys = key.split(".")
        current = self.metadata
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        final_key = keys[-1]
        if final_key in current and isinstance(current[final_key], dict) and isinstance(value, dict):
            self.merge_json2(current[final_key], value)
        else:
            current[final_key] = value

    def extract(self):
        if self.format == "json":
            return json.dumps(self.metadata, indent=4)
        elif self.format == "yaml":
            return yaml.dump(self.metadata, indent=4)

    def process_tpr(self, file_path):

        def build_gmx_dump_command(file_path):
            # "-section", "inputrec", "-section", "qm-opts", "-section", "grpopts", "-section", "header", "-section", "box", "-section", "box_rel", "-section", "boxv", "-section", "pres_prev", "-section", "svir_prev", "-section", "fvir_prev", "-section", "nosehoover_xi", "-section", "group_statistics"
            command = [self.gmx_bin, "dump", "-s", file_path, "-format", self.format]
            for section in self.gmx_dump_options:
                command.append(f'-section')
                command.append(section)
            return command
        
        cmd = build_gmx_dump_command(file_path)
        if self.verbose:
            print(f"Running command: {cmd}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            error = result.stderr
            try:
                m = re.search(r'Reading file .*, VERSION (.*) \(.*\)', error)
                version = m.group(1)
            except:
                version = None

            self._put_metadata("simulation", json.loads(result.stdout))
            self._put_metadata("administrative.software_information", {"software": "GROMACS", "version": version})
    
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr}")
            return {"error": f"Failed to process .tpr file: {e.stderr}"}

    def process_gro(self, file_path):
        try:
            result = [float(n) for n in open(file_path, "r").readlines()[-1].rstrip().split()]
            self._put_metadata("system.box_size_and_shape", result)
        except Exception as e:
            return {"error": f"Failed to process .gro file: {str(e)}"}

    def process_top(self, file_path):
        try:
            with open(file_path, "r") as f:
                content = f.read()

            match = re.search(r'"(amber\d+)\.ff/forcefield\.itp"', content)
            if match:
                self._put_metadata("simulation.forcefield", match.group(1))

            water_topology_pattern = r'\; Include water topology\n#include\s".*\.ff\/(.*)\.itp"'
            water_topology_match = re.search(water_topology_pattern, content)
            if water_topology_match:
                self._put_metadata("system.water_model", water_topology_match.group(1))

        except Exception as e:
            return {"error": f"Failed to process .top file: {str(e)}"}
        
    def process_opt(self, file_path):
        try:
            metadata = {}

            with open(file_path, "r") as f:
                content = f.read()
            
            if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                metadata = yaml.safe_load(content)
            else:
                metadata = json.loads(content)

            if "administrative" in metadata:
                self._put_metadata("administrative", metadata["administrative"])
            if "simulated_object" in metadata:
                self._put_metadata("simulated_object", metadata["simulated_object"])
        except Exception as e:
            return {"error": f"Failed to process .opt file: {str(e)}"}
        
    def process_archive(self, file_path):
        if not os.path.isfile(file_path):
            return {"error": f"File {file_path} does not exist."}
        if not self._allowed_file(file_path):
            return {"error": f"File {file_path} has an invalid extension."}

        if file_path.endswith((".zip", ".tar", ".gz", ".bz2")):
            extract_dir = self.extract_archive(file_path)
            for root, _, files in os.walk(extract_dir.name):
                for file in files:
                    if self._allowed_file(file):
                        file_path = os.path.join(root, file)
                        if file.endswith(".tpr"):
                            self.process_tpr(file_path)
                        elif file.endswith(".gro"):
                            self.process_gro(file_path)
                        elif file.endswith(".top"):
                            self.process_top(file_path)
                        elif file.endswith(".json") or file.endswith(".yaml") or file.endswith(".yml"):
                            self.process_opt(file_path)
            extract_dir.cleanup()
        else:
            return {"error": "Unsupported archive format."}
        
    def extract_archive(self, file_path):
        try:
            extract_dir = tempfile.TemporaryDirectory()

            if file_path.endswith(".zip"):
                with zipfile.ZipFile(file_path, "r") as zf:
                    zf.extractall(extract_dir.name)
            else:
                with tarfile.open(file_path, "r:*") as tf:
                    tf.extractall(extract_dir.name)

            return extract_dir
        except Exception as e:
            print(Exception(f"Failed to process archive file: {str(e)}"))