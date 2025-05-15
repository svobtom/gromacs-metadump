"""
Description: This script extracts metadata from GROMACS TPR files acording to the schema
Author: Adrian Rosinec, and Ondrej Schindler
Maintainer: Adrian Rosinec
Email: adrian@ics.muni.cz
Dependencies: Python 3.8+, GROMACS 2020.4+ (with extension of dump tool), GromacsMetadataExtractor 0.1+
Version: 1.0
Python Version: 3.8+
License: BSD 3-Clause License

Usage:

    $ python3 gmxextract.py --tpr <path to TPR file>

Arguments:

    --tpr: Path to TPR file from GROMACS with metadata. (Obligatory argument)
    --gro: Path to GRO file from GROMACS with metadata. 
    --top: Path to TOP file from GROMACS with metadata.
    --opt: Path to optional metadata for extending metadata.
    --gmx_bin: Path to GROMACS binary used to parse the metadata. Default: /opt/gromacs/bin/gmx
    --archive: Path to archive with files. If provided, the script will process all files in the archive.
    --verbose: If true, verbose information is printed as script runs. Default: False
    --format: Print extracted metadata as `json` or `yaml` formats. Default: json

"""

import argparse
import os

from GromacsMetadataExtractor import GromacsMetadataExtractor

def load_argumets():
        parser = argparse.ArgumentParser()
        parser.add_argument('--tpr',
                            type=str,
                            help='Tpr file from GROMACS with metadata. (Obligatory argument)')
        parser.add_argument('--gro',
                            type=str,
                            help='Gro file from GROMACS with metadata.')
        parser.add_argument('--top',
                            type=str,
                            help='Cpt file from GROMACS with metadata.',
                            default=None)
        parser.add_argument('--opt',
                            type=str,
                            help='Optional metadata for extending metadata.',
                            default=None) 
        parser.add_argument('--format',
                            type=str,
                            choices=("json", "yaml"),
                            default="json",
                            help="Print extracted metadata as json or yaml formats.")
        parser.add_argument('--gmx_bin',
                            type=str,
                            default="/opt/gromacs/bin/gmx",
                            help="Path to GROMACS binary used to parse the metadata. Default: gmx")
        parser.add_argument('--archive',
                            type=str,
                            default=None,
                            help="Path to archive with files.")
        parser.add_argument('--verbose',
                            action="store_true",
                            help="If true, verbose information is printed as script runs.")

        args = parser.parse_args()
        if args.archive:
            if not os.path.isfile(args.archive):
                exit(f"\nERROR! There is no archive file {args.archive}!\n")
        else:
            if not args.tpr:
                exit(f"\nERROR! The following argument is obligatory: --tpr!\n")
        return args

if __name__ == "__main__":   
    """
        Usage:
            python3 GromacsMetadataExtractor.py --tpr_file <tpr_file> [--gro_file <gro_file> --cpt_file <cpt_file> --format <json|yaml>]
        """
    args = load_argumets()

    metadump = GromacsMetadataExtractor(format=args.format, verbose=args.verbose, gmx_bin=args.gmx_bin)
    if args.archive:
         metadump.process_archive(args.archive)
    else:
        if args.tpr:
            metadump.process_tpr(args.tpr)
        if args.gro:
            metadump.process_gro(args.gro)
        if args.top:
            metadump.process_top(args.top)
        if args.opt:
            metadump.process_opt(args.opt)

    print(metadump.extract())