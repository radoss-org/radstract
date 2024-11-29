import json
import os
import tempfile

import numpy as np
from PIL import Image

from radstract.data.dicom import DicomTypes
from radstract.datasets.huggingface import convert_dataset_to_huggingface
from radstract.datasets.nnunet import (
    build_nnunet_dir_structure,
    convert_dataset_to_nnunet,
    generate_nnunet_dataset_json,
)
from radstract.datasets.polygon import convert_dataset_to_polygons
from radstract.datasets.utils import DataSplit

POST_DATASET_DIR = "./tests/test_data/post_created_datasets"

TEST_DIR_HUGGINGFACE = f"{POST_DATASET_DIR}/huggingface"
TEST_DIR_NNUNET = f"{POST_DATASET_DIR}/nnunet"
TEST_DIR_POLYGON = f"{POST_DATASET_DIR}/polygon"


# def test_polygon_dataset(dataset_dir):
#     # create temp dir
#     with tempfile.TemporaryDirectory() as temp_dir:

#         convert_dataset_to_polygons(
#             input_dir=dataset_dir,
#             output_dir=temp_dir,
#             processes=8,
#             crop_coordinates=None,
#             dicom_type=DicomTypes.SERIES,
#             data_split=DataSplit(0.5, 0.5, 0),
#             color_changes=None,
#             min_polygons=6,
#         )

#         temp_dir_files = sorted(os.listdir(f"{temp_dir}/labels/train"))
#         test_dir_files = sorted(os.listdir(f"{TEST_DIR_POLYGON}/labels/train"))

#         assert temp_dir_files == test_dir_files

#         with open(f"{temp_dir}/labels/train/{temp_dir_files[0]}", "r") as f:
#             temp_dir_file = f.read()

#         with open(
#             f"{TEST_DIR_POLYGON}/labels/train/{test_dir_files[0]}", "r"
#         ) as f:
#             test_dir_file = f.read()

#         assert temp_dir_file == test_dir_file


# def test_huggingface_dataset(dataset_dir):
#     with tempfile.TemporaryDirectory() as temp_dir:
#         convert_dataset_to_huggingface(
#             input_dir=dataset_dir,
#             output_dir=temp_dir,
#             processes=8,
#             crop_coordinates=None,
#             dicom_type=DicomTypes.SERIES,
#             data_split=DataSplit(0.5, 0.5, 0),
#             color_changes=None,
#         )

#         temp_dir_files = sorted(os.listdir(f"{temp_dir}/labels/train"))
#         test_dir_files = sorted(os.listdir(f"{TEST_DIR_POLYGON}/labels/train"))

#         assert temp_dir_files == test_dir_files

#         temp_img = Image.open(f"{temp_dir}/labels/train/{temp_dir_files[0]}")
#         test_img = Image.open(
#             f"{TEST_DIR_HUGGINGFACE}/labels/train/{test_dir_files[0]}"
#         )

#         assert np.array_equal(np.array(temp_img), np.array(test_img))


def test_nnunet_dataset(dataset_dir):
    with tempfile.TemporaryDirectory() as temp_dir:
        convert_dataset_to_nnunet(
            input_dir=dataset_dir,
            output_dir=temp_dir,
            processes=8,
            crop_coordinates=None,
            dicom_type=DicomTypes.SERIES,
            data_split=DataSplit(0.5, 0, 0.5),
            color_changes=None,
        )

        nnunet_dir_structure = build_nnunet_dir_structure(temp_dir)

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

        with open(f"{temp_dir}/dataset.json", "w") as f:
            json.dump(dataset_json, f, indent=4)

        with open(f"{temp_dir}/dataset.json", "r") as f:
            temp_dir_file = f.read()

        with open(f"{TEST_DIR_NNUNET}/dataset.json", "r") as f:
            test_dir_file = f.read()

        assert temp_dir_file == test_dir_file
