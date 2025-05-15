"""
Description: This script extracts metadata from GROMACS TPR files acording to the schema
Author: Adrian Rosinec, and Ondrej Schindler
Maintainer: Adrian Rosinec
Email: adrian@ics.muni.cz
Dependencies: Python 3.8+, GROMACS 2020.4+, GromacsMetadataExtractor 0.1+
Version: 1.0
Python Version: 3.8+
License: BSD 3-Clause License

Usage:

    $ python3 extract.py --tpr_file <path to TPR file>

Arguments:

    --tpr_file: Path to TPR file from GROMACS with metadata. (Obligatory argument)
    --gro_file: Path to GRO file from GROMACS with metadata. (Unnused argument)
    --cpt_file: Path to CPT file from GROMACS with metadata. (Unnused argument)
    --format: Print extracted metadata as `json` or `yaml` formats. Default: json
    --debug: If true, debug information is printed as script runs. Default: False

"""

from GromacsMetadataExtractor import MetadataExtractor
import argparse
import os

def load_argumets():
        parser = argparse.ArgumentParser()
        parser.add_argument('--tpr_file',
                            type=str,
                            help='Tpr file from GROMACS with metadata. (Obligatory argument)',
                            required=True)
        parser.add_argument('--gro_file',
                            type=str,
                            help='Gro file from GROMACS with metadata.')
        parser.add_argument('--cpt_file',
                            type=str,
                            help='Cpt file from GROMACS with metadata.',
                            default=None)
        parser.add_argument('--format',
                            type=str,
                            choices=("json", "yaml"),
                            default="json",
                            help="Print extracted metadata as json or yaml formats.")
        parser.add_argument('--debug',
                            type=bool,
                            default=False,
                            help="If true, debug information is printed as script runs.")

        args = parser.parse_args()
        if not os.path.isfile(args.tpr_file):
            exit(f"\nERROR! There is no file {args.tpr_file}!\n")
        return args

if __name__ == "__main__":   
    """
        Usage:
            python3 GromacsMetadataExtractor.py --tpr_file <tpr_file> [--gro_file <gro_file> --cpt_file <cpt_file> --format <json|yaml>]
        """
    args = load_argumets()

    e = MetadataExtractor(args.tpr_file, args.gro_file, None, False).run()
    print(args.debug)
    e.debug = args.debug
    print(e.print(args.format))