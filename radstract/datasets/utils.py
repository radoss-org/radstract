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

import logging
import os
from collections import defaultdict
from multiprocessing import Lock, Manager, Pool
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pydicom
from PIL import Image

from radstract.data.colors import change_color
from radstract.data.dicom import DicomTypes, convert_dicom_to_images
from radstract.data.multimodal import remove_black_frames
from radstract.data.nifti import convert_nifti_to_image_labels


class DataSplit:
    def __init__(self, pc_train=None, pc_val=None, pc_test=None):
        if pc_train is None and pc_val is None and pc_test is None:
            pc_train = 0.7
            pc_val = 0.2
            pc_test = 0.1

        if pc_train * 10 + pc_val * 10 + pc_test * 10 != 10:
            raise ValueError(
                "The sum of the percentages must be equal to 1."
                f"The current sum is: {(pc_train*10 + pc_val*10 + pc_test*10)/10}"
            )
        self.pc_train = pc_train
        self.pc_val = pc_val
        self.pc_test = pc_test


def _process_dicom_nifti_pair(
    dcm_path: str,
    nii_path: str,
    crop_coordinates: Tuple[int, int, int, int],
    dicom_type: DicomTypes,
    color_changes: List[Tuple[int, int, int]],
) -> Tuple[List[Image.Image], List[Image.Image]]:
    """
    @private
    Process a DICOM and NIfTI file pair.

    :param dcm_path: str: Path to the DICOM file.
    :param nii_path: str: Path to the NIfTI file.
    :param crop_coordinates: tuple: Crop coordinates for the images.
    :param dicom_type: DicomTypes: Type of DICOM file.
    :param color_changes: list: List of colour changes.

    :return: tuple: Processed DICOM and NIfTI images.
    """
    dicom_images = convert_dicom_to_images(
        pydicom.dcmread(dcm_path),
        crop_coordinates=crop_coordinates,
        dicom_type=dicom_type,
    )
    nifti_images, _ = convert_nifti_to_image_labels(
        nii_path, crop_coordinates=crop_coordinates
    )

    dicom_images, nifti_images = remove_black_frames(dicom_images, nifti_images)

    new_nifti_images = []

    for seg_image in nifti_images:
        if color_changes:
            for old_color, new_color in color_changes:
                seg_image = change_color(
                    img=seg_image, old_color=old_color, new_color=new_color
                )

        new_nifti_images.append(seg_image)

    return dicom_images, new_nifti_images


def save_image_label_pair(
    image: Image.Image,
    label: Image.Image,
    image_dir: str,
    label_dir: str,
    file_name: str,
    _: None = None,
):
    """
    Save an image and label pair.

    :param image: PIL.Image: Image to save.
    :param label: PIL.Image: Label to save.
    :param image_dir: str: Directory to save the image.
    :param label_dir: str: Directory to save the label.
    :param file_name: str: File name for the image and label.
    :param _: None: Placeholder for the file_pair_kwargs.
    :return: None
    """
    image.save(os.path.join(image_dir, f"{file_name}.jpg"), "JPEG")
    label.save(os.path.join(label_dir, f"{file_name}.png"))


def _process_file_pair_with_split(
    input_dir: str,
    output_dir: str,
    crop_coordinates: Tuple[int, int, int, int],
    dicom_type: DicomTypes,
    pair_key: str,
    pair: Dict[str, str],
    split: str,
    color_changes: List[Tuple[int, int, int]],
    file_pair_kwargs: Optional[Dict],
    save_func=save_image_label_pair,
    single_image_process: bool = True,
):
    """
    @private
    Process a single file pair for a specific data split.

    :param input_dir: str: Path to the input directory.
    :param output_dir: str: Path to the output directory.
    :param crop_coordinates: tuple: Crop coordinates for the images.
    :param dicom_type: DicomTypes: Type of DICOM file.
    :param pair_key: str: Key for the file pair.
    :param pair: dict: Dictionary containing the file pair.
    :param split: str: Data split (train, val, or test).
    :param color_changes: list: List of colour changes.
    :param file_pair_kwargs: dict: Keyword arguments for the file pair.
    :param save_func: function: Function to save the image and label pair.
    :param single_image_process: bool: Process a single image.

    :return: None
    """
    image_dir = os.path.join(output_dir, "images", split)
    label_dir = os.path.join(output_dir, "labels", split)

    if pair["dcm"] and pair["nii"]:
        dcm_path = os.path.join(input_dir, pair["dcm"])
        nii_path = os.path.join(input_dir, pair["nii"])

        dicom_images, nifti_images = _process_dicom_nifti_pair(
            dcm_path, nii_path, crop_coordinates, dicom_type, color_changes
        )

        if single_image_process:
            for i, (dicom_image, seg_image) in enumerate(
                zip(dicom_images, nifti_images)
            ):
                file_name = f"{pair_key}_{i}"
                save_func(
                    dicom_image,
                    seg_image,
                    image_dir,
                    label_dir,
                    file_name,
                    file_pair_kwargs,
                )
        else:
            file_name = pair_key
            save_func(
                dicom_images,
                nifti_images,
                image_dir,
                label_dir,
                file_name,
                file_pair_kwargs,
            )

        logging.info(f"Processed pair: {pair}")
    else:
        logging.warning(f"Incomplete pair found: {pair}")


def convert_dcm_nii_dataset(
    input_dir: str,
    output_dir: str,
    processes: int = 1,
    crop_coordinates: Tuple[int, int, int, int] = None,
    dicom_type: DicomTypes = DicomTypes.DEFAULT,
    data_split: Tuple[float, float] = (0.3, 0.4),
    color_changes: List[Tuple[int, int, int]] = None,
    file_pair_kwargs: Optional[Dict] = None,
    save_func=save_image_label_pair,
    single_image_process: bool = True,
    datasplit_seed=42,
):
    """
    Convert a dataset of DICOM and NIfTI files with consistent data splitting.

    :param input_dir: str: Path to the input directory.
    :param output_dir: str: Path to the output directory.
    :param processes: int: Number of processes to use.
    :param crop_coordinates: tuple: Crop coordinates for the images.
    :param dicom_type: DicomTypes: Type of DICOM file.
    :param data_split: tuple: Data split percentages.
    :param color_changes: list: List of colour changes.
    :param file_pair_kwargs: dict: Keyword arguments for the file pair.
    :param save_func: function: Function to save the image and label pair.
    :param single_image_process: bool: Process a single image.
    :param datasplit_seed: int: Seed for the data split.

    :return: None
    """
    file_pairs = defaultdict(lambda: {"dcm": None, "nii": None})

    for file in sorted(os.listdir(input_dir)):
        if file.endswith(".dcm") or file.endswith(".nii.gz"):
            key = file.split(".")[0]
            if file.endswith(".dcm"):
                file_pairs[key]["dcm"] = file
            elif file.endswith(".nii.gz"):
                file_pairs[key]["nii"] = file

    pairs_to_process = [(pair_key, pair) for pair_key, pair in file_pairs.items()]

    # shuffle the pairs based on the seed
    rng = np.random.default_rng(datasplit_seed)
    rng.shuffle(pairs_to_process)

    # Pre-determine data splits
    total_files = len(pairs_to_process)
    # if the data_split is a tuple, convert it to a DataSplit object
    if isinstance(data_split, tuple):
        pc_train, pc_val = data_split
        pc_test = 1 - pc_train - pc_val
    else:
        pc_train = data_split.pc_train
        pc_val = data_split.pc_val
        pc_test = data_split.pc_test

    # verify that the percentages add up to 1
    if pc_train * 10 + pc_val * 10 + pc_test * 10 != 10:
        raise ValueError(
            "The sum of the percentages must be equal to 1."
            f"The current sum is: {(pc_train*10 + pc_val*10 + pc_test*10)/10}"
        )

    train_count = int(pc_train * total_files)
    val_count = int(pc_val * total_files)

    train_pairs = pairs_to_process[:train_count]
    val_pairs = pairs_to_process[train_count : train_count + val_count]
    test_pairs = pairs_to_process[train_count + val_count :]

    # if pc_test is 0, but there are still test pairs, add them to the training set
    if pc_test == 0 and test_pairs:
        train_pairs.extend(test_pairs)
        test_pairs = []

    # Assign directories to the splits
    split_mapping = []
    for pair in train_pairs:
        split_mapping.append(("train", pair))
    for pair in val_pairs:
        split_mapping.append(("val", pair))
    for pair in test_pairs:
        split_mapping.append(("test", pair))

    # Use multiprocessing to process file pairs
    with Pool(processes=processes) as pool:
        pool.starmap(
            _process_file_pair_with_split,
            [
                (
                    input_dir,
                    output_dir,
                    crop_coordinates,
                    dicom_type,
                    pair_key,
                    pair,
                    split,
                    color_changes,
                    file_pair_kwargs,
                    save_func,
                    single_image_process,
                )
                for split, (pair_key, pair) in split_mapping
            ],
        )
