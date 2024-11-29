"""
Example of using the NNUNET, Polygon and Huggingface datasets

Note that there is an assumption that all your data is in a
single folder, with the following structure:

./input_dir
├── file1.dcm
├── file1.nii.gz
├── file2.dcm
├── file2.nii.gz

Each file pair should have the same name, with the DICOM
file ending in .dcm and the NIfTI file ending in .nii.gz.
"""

import json
import os

from radstract.data.dicom import DicomTypes
from radstract.datasets.huggingface import convert_dataset_to_huggingface
from radstract.datasets.nnunet import (
    build_nnunet_dir_structure,
    convert_dataset_to_nnunet,
    generate_nnunet_dataset_json,
)
from radstract.datasets.polygon import convert_dataset_to_polygons
from radstract.datasets.utils import DataSplit
from radstract.testdata import Cases, download_case

dcm_file, *_ = download_case(Cases.ULTRASOUND_DICOM_DATASET)

DATASET_DIR = os.path.join(os.path.dirname(dcm_file))
OUTPUT_DIR = "./debug/dataset"

polygon_dir = os.path.join(OUTPUT_DIR, "polygon")
huggingface_dir = os.path.join(OUTPUT_DIR, "huggingface")
nnunet_dir = os.path.join(OUTPUT_DIR, "nnunet")

convert_dataset_to_polygons(
    input_dir=DATASET_DIR,
    output_dir=polygon_dir,
    processes=8,
    crop_coordinates=None,
    dicom_type=DicomTypes.SERIES,
    data_split=DataSplit(0.5, 0.5, 0),
    color_changes=None,
    min_polygons=6,
)

convert_dataset_to_huggingface(
    input_dir=DATASET_DIR,
    output_dir=huggingface_dir,
    processes=8,
    crop_coordinates=None,
    dicom_type=DicomTypes.SERIES,
    data_split=DataSplit(0.5, 0.5, 0),
    color_changes=None,
)

convert_dataset_to_nnunet(
    input_dir=DATASET_DIR,
    output_dir=nnunet_dir,
    processes=8,
    crop_coordinates=None,
    dicom_type=DicomTypes.SERIES,
    data_split=DataSplit(0.5, 0, 0.5),
    color_changes=None,
)

nnunet_dir_structure = build_nnunet_dir_structure(nnunet_dir)

dataset_json = generate_nnunet_dataset_json(
    nnunet_dir_structure,
    dataset_name="HipUltrasound",
    modalities={0: "US"},
    labels={
        0: "Background",
    },
    description="Dataset for Hip Ultrasound",
    reference="Put your reference here",
    licence="Dataset license",
    release="1.0",
)

with open(f"{nnunet_dir}/dataset.json", "w") as f:
    json.dump(dataset_json, f, indent=4)
