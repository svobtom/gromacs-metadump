"""
Description: This script extracts metadata from Gromacs TPR files acording to the schema
Author: Adrian Rosinec, and Ondrej Sindler
Maintainer: Adrian Rosinec
Email: adrian@ics.muni.cz
Date Created: February 13, 2023
Date Modified: January 1, 2024
Dependencies: Python 3.8+, Gromacs 2020.4+, GromacsMetadataExtractor 0.1+
Version: 0.1
Python Version: 3.8+
License: BSD 3-Clause License

Usage:

    $ pytohn3 extract.py --tpr_file <path to TPR file>

Arguments:

    --tpr_file: Path to TPR file from Gromacs with metadata. (Obligatory argument)
    --gro_file: Path to GRO file from Gromacs with metadata. (Unnused argument)
    --cpt_file: Path to CPT file from Gromacs with metadata. (Unnused argument)
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
                            help='Tpr file from gromacs with metadata. (Obligatory argument)',
                            required=True)
        parser.add_argument('--gro_file',
                            type=str,
                            help='Gro file from gromacs with metadata.')
        parser.add_argument('--cpt_file',
                            type=str,
                            help='Cpt file from gromacs with metadata.',
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