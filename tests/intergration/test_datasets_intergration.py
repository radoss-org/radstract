# Copyright 2024 Adam McArthur
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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


def test_polygon_dataset(dataset_dir):
    # create temp dir
    with tempfile.TemporaryDirectory() as temp_dir:

        convert_dataset_to_polygons(
            input_dir=dataset_dir,
            output_dir=temp_dir,
            processes=8,
            crop_coordinates=None,
            dicom_type=DicomTypes.SERIES,
            data_split=DataSplit(0.5, 0.5, 0),
            color_changes=None,
            min_polygons=6,
        )

        temp_dir_files = sorted(os.listdir(f"{temp_dir}/labels/train"))
        test_dir_files = sorted(os.listdir(f"{TEST_DIR_POLYGON}/labels/train"))

        assert temp_dir_files == test_dir_files

        with open(f"{temp_dir}/labels/train/{temp_dir_files[0]}", "r") as f:
            temp_dir_file = f.read()

        with open(
            f"{TEST_DIR_POLYGON}/labels/train/{test_dir_files[0]}", "r"
        ) as f:
            test_dir_file = f.read()

        assert temp_dir_file == test_dir_file


def test_huggingface_dataset(dataset_dir):
    with tempfile.TemporaryDirectory() as temp_dir:
        convert_dataset_to_huggingface(
            input_dir=dataset_dir,
            output_dir=temp_dir,
            processes=8,
            crop_coordinates=None,
            dicom_type=DicomTypes.SERIES,
            data_split=DataSplit(0.5, 0.5, 0),
            color_changes=None,
        )

        temp_dir_files = sorted(os.listdir(f"{temp_dir}/labels/train"))
        test_dir_files = sorted(
            os.listdir(f"{TEST_DIR_HUGGINGFACE}/labels/train")
        )

        assert temp_dir_files == test_dir_files

        temp_img = Image.open(f"{temp_dir}/labels/train/{temp_dir_files[0]}")
        test_img = Image.open(
            f"{TEST_DIR_HUGGINGFACE}/labels/train/{test_dir_files[0]}"
        )

        assert np.array_equal(np.array(temp_img), np.array(test_img))


def test_nnunet_dataset(dataset_dir):
    with tempfile.TemporaryDirectory() as temp_dir:
        convert_dataset_to_nnunet(
            input_dir=dataset_dir,
            output_dir=temp_dir,
            processes=8,
            crop_coordinates=None,
            dicom_type=DicomTypes.SERIES,
            data_split=DataSplit(0.5, 0.5, 0),
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


def test_consistent_dataset_splits(dataset_dir):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Convert dataset to each format
        convert_dataset_to_polygons(
            input_dir=dataset_dir,
            output_dir=f"{temp_dir}/polygon",
            processes=8,
            crop_coordinates=None,
            dicom_type=DicomTypes.SERIES,
            data_split=DataSplit(0.5, 0.5, 0),
            color_changes=None,
            min_polygons=6,
        )

        convert_dataset_to_huggingface(
            input_dir=dataset_dir,
            output_dir=f"{temp_dir}/huggingface",
            processes=8,
            crop_coordinates=None,
            dicom_type=DicomTypes.SERIES,
            data_split=DataSplit(0.5, 0.5, 0),
            color_changes=None,
        )

        convert_dataset_to_nnunet(
            input_dir=dataset_dir,
            output_dir=f"{temp_dir}/nnunet",
            processes=8,
            crop_coordinates=None,
            dicom_type=DicomTypes.SERIES,
            data_split=DataSplit(0.5, 0.5, 0),
            color_changes=None,
        )

        # Helper function to strip extensions
        def strip_extensions(file_set):
            return {
                os.path.splitext(file)[0].split("_")[0].replace(".nii", "")
                for file in file_set
            }

        # Load splits and strip extensions
        polygon_train_ids = strip_extensions(
            os.listdir(f"{temp_dir}/polygon/images/train")
        )
        polygon_val_ids = strip_extensions(
            os.listdir(f"{temp_dir}/polygon/images/val")
        )
        polygon_test_ids = strip_extensions(
            os.listdir(f"{temp_dir}/polygon/images/test")
        )

        huggingface_train_ids = strip_extensions(
            os.listdir(f"{temp_dir}/huggingface/images/train")
        )
        huggingface_val_ids = strip_extensions(
            os.listdir(f"{temp_dir}/huggingface/images/val")
        )
        huggingface_test_ids = strip_extensions(
            os.listdir(f"{temp_dir}/huggingface/images/test")
        )

        nnunet_train_ids = strip_extensions(
            os.listdir(f"{temp_dir}/nnunet/imagesTr")
        )
        nnunet_test_ids = strip_extensions(
            os.listdir(f"{temp_dir}/nnunet/imagesTs")
        )

        # Assert consistency across formats
        assert polygon_train_ids == huggingface_train_ids == nnunet_train_ids
        assert polygon_val_ids == huggingface_val_ids == nnunet_test_ids
        assert polygon_test_ids == huggingface_test_ids
