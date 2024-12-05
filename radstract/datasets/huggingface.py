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

import os
import random
from typing import List, Tuple, Union

from datasets import Dataset, DatasetDict
from datasets import Image as HuggingfaceImage

from radstract.data.dicom import DicomTypes

from .utils import convert_dcm_nii_dataset, save_image_label_pair


def convert_dataset_to_huggingface(
    input_dir: str,
    output_dir: str,
    processes: int = 1,
    crop_coordinates: Tuple[int, int, int, int] = None,
    dicom_type: DicomTypes = DicomTypes.DEFAULT,
    data_split: Tuple[float, float] = (0.3, 0.4),
    color_changes: List[Tuple[int, int, int]] = None,
    datasplit_seed=42,
) -> None:
    """
    Convert a dataset in the input_dir to a Huggingface DatasetDict and save it to the output_dir.

    :param input_dir: str: Path to the input directory.
    :param output_dir: str: Path to the output directory.
    :param processes: int: Number of processes to use.
    :param crop_coordinates: tuple: Crop coordinates for the images.
    :param dicom_type: DicomTypes: Type of DICOM file.
    :param data_split: tuple: Data split percentages.
    :param color_changes: list: List of colour changes.
    :param min_polygons: int: Minimum number of polygons to consider.
    :param datasplit_seed: int: Seed for the data split.

    :return: None
    """

    # create the output directory, train, val and test directories
    os.makedirs(output_dir, exist_ok=True)
    for split in ["images", "labels"]:
        os.makedirs(os.path.join(output_dir, split), exist_ok=True)
        for split_dir in ["train", "val", "test"]:
            os.makedirs(
                os.path.join(output_dir, split, split_dir), exist_ok=True
            )

    # Convert the dataset to a Huggingface DatasetDict
    convert_dcm_nii_dataset(
        input_dir,
        output_dir,
        processes=processes,
        crop_coordinates=crop_coordinates,
        dicom_type=dicom_type,
        data_split=data_split,
        color_changes=color_changes,
        file_pair_kwargs=None,
        save_func=save_image_label_pair,
        datasplit_seed=datasplit_seed,
    )


def make_huggingface_datadict(
    dataset_dir: str, dataset_fraction: int = 1.0
) -> DatasetDict:
    """
    Create a Huggingface DatasetDict from a dataset directory.

    :param dataset_dir: str: Path to the dataset directory.
    :param dataset_fraction: float: Fraction of the dataset to use.

    :return: DatasetDict: Huggingface DatasetDict.
    """

    def get_dataset_paths(data_type, file_type, extension):
        paths = []
        data_path = os.path.join(dataset_dir, file_type, data_type)
        for root, _, files in os.walk(data_path):
            for file in files:
                if file.endswith(extension):
                    paths.append(os.path.join(root, file))
        # Shuffle and select a fraction of the dataset
        random.shuffle(paths)
        return paths[: int(len(paths) * dataset_fraction)]

    image_paths_train = get_dataset_paths("train", "images", ".jpg")
    label_paths_train = get_dataset_paths("train", "labels", ".png")
    image_paths_validation = get_dataset_paths("val", "images", ".jpg")
    label_paths_validation = get_dataset_paths("val", "labels", ".png")

    def create_dataset(image_paths, label_paths):
        dataset_test = Dataset.from_dict(
            {"image": sorted(image_paths), "label": sorted(label_paths)}
        )
        dataset_test = dataset_test.cast_column("image", HuggingfaceImage())
        dataset_test = dataset_test.cast_column("label", HuggingfaceImage())

        return dataset_test

    # step 1: create Dataset objects
    train_dataset = create_dataset(image_paths_train, label_paths_train)
    validation_dataset = create_dataset(
        image_paths_validation, label_paths_validation
    )

    # step 2: create DatasetDict
    dataset = DatasetDict(
        {
            "train": train_dataset,
            "validation": validation_dataset,
        }
    )

    return dataset
