## Radstract

Radstract is python library containing shared code for RadOSS projects.

It has a range of subpackages for different tasks:
- Data: For data/image manipulation and conversion functions
- Analysis: For different methods of analyzing the data, from nifti and dicom files
- Math: For different mathematical functions and operations
- Datasets: for converting and working with different datasets (Huggingface etc)

Feel free to use this code in your own projects, and if you have any questions or suggestions, please feel free to open an issue.

## Installation

```bash
pip install git+https://github.com/radoss-org/radstract.git
```

See examples here for a quickstart: https://github.com/radoss-org/Radstract/tree/main/examples

## Docs

The Docs currently have to be built locally, and can be done so by running the following command:

```bash
git clone https://github.com/radoss-org/radstract.git
cd radstract

# For running scripts
pip install poethepoet

poetry install

# create and open docs in browser
poe viewdocs
```

## Examples

See examples here: https://github.com/radoss-org/Radstract/tree/main/examples


## Developer Guide

You can clone the repository and install the dependencies with the following command:

```bash
git clone https://github.com/radoss-org/radstract.git
```

You can then install retuve with poetry, and then run the tests:

```bash
# Needed for the scripts
pip install poethepoet

cd retuve
poetry install

# Generate the test data
poe testgen

# Run all tests, including examples.
poe test_all

# Get info on all other dev scripts
poe help
```

## Acknowledgments

Data for the examples and tests is from https://github.com/radoss-org/radoss-creative-commons.

Please see this repo for attribution and licensing information.

- **Shape Distribution Models** From https://graphics.stanford.edu/courses/cs468-08-fall/pdf/osada.pdf

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.