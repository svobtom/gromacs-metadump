# GROMACS MetaDump CLI

This is the CLI utility that extracts the metadata from the molecular dynamics simulations produced by the GROMACS software.

This functionality is also available as web application at https://gmd.ceitec.cz, where it is possible to obtain metadata after uploading a TPR file without need to install or run local any scripts.

## Dependencies

- GROMACS software with extended dump utility (`gmx dump`) is required. It has to be built from source code using `freeze/v2025.1` branch available in the repository https://github.com/sb-ncbr/gromacs.git.
- Python 3.8 or greater

## Usage

How to use the GROMACS MetaDump software.

### Basic usage from CLI

```bash
python3 gmxextract.py --tpr <path to TPR file>
```

### Specify other input files, format and GROMACS binary
```bash
python3 gmxextract.py --tpr /data/run.tpr --gro /data/run.gro --top /data/topol.top --opt /data/optional.json --gmx_bin /opt/gromacs2023/bin/gmx --format json
```

### Specify archive as input file, format and GROMACS binary
```bash
python3 gmxextract.py --archive /data/archive.zip --gmx_bin /opt/gromacs2023/bin/gmx --format json
```

#### Available arguments

| Argument      | Description                              | Example                          |
|---------------|------------------------------------------|----------------------------------|
|   --tpr  |   Path to the TPR file                   |  --tpr run.tpr   |
|   --top  |   Path to the TOP file                   |  --top topol.top           |
|   --gro  |   Path to the GRO file                   |  --gro run.gro              |
|   --opt  |  Path to optional metadata json/yaml     |  --opt optional.json                    |
|   --gmx_bin  |  Path to custom GROMACS software     |  --gmx_bin /opt/gromacs/bin/gmx                         |
|   --archive | If all required files are in archive (.zip, .tar(.gz)) | --archive archive.zip  |
|   --format    |   Format of output metadata <json/yaml>  |  --format json                   |
|   --verbose     |    Print verbose information <switch>  |  --verbose                    |

If `--archive` is specified, all other input files (`--tpr`, `--top`, `--gro`, and `--opt`) will be ignored.

## Trying it out in Docker
If you want to try the GROMACS MetaDump software but don't want to install anything, you can use the ready-made Docker image.

```bash
docker run --rm -v /path/to/simulation/files:/data:/data cerit.io/ceitec-biodata-pub/gromacs-metadump-worker python3 gmxextract.py --tpr <path to TPR file>
```

## Authors
- Adrián Rošinec - adrian@muni.cz
- Ondřej Schindler - ondrej.schindler@mail.muni.cz

## License
BSD 3-Clause License, see LICENSE file

Copyright (c) 2025, Masaryk University.
All rights reserved.
