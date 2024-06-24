import logging
import os
from collections import defaultdict
from multiprocessing import Pool
from typing import Dict, List, Optional, Tuple

import numpy as np
import pydicom
from PIL import Image

from radstract.data.colors import change_color
from radstract.data.dicom import DicomTypes, convert_dicom_to_images
from radstract.data.multimodal import remove_black_frames
from radstract.data.nifti import convert_nifti_to_image_labels


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

    dicom_images, nifti_images = remove_black_frames(
        dicom_images, nifti_images
    )

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


def _process_file_pair(
    input_dir: str,
    output_dir: str,
    crop_coordinates: Tuple[int, int, int, int],
    dicom_type: DicomTypes,
    pair_key: str,
    pair: Dict[str, str],
    data_split: Tuple[float, float],
    color_changes: List[Tuple[int, int, int]],
    file_pair_kwargs: Optional[Dict],
    save_func=save_image_label_pair,
    single_image_process: bool = True,
):
    """
    @private
    Process a single file pair.

    :param input_dir: str: Path to the input directory.
    :param output_dir: str: Path to the output directory.
    :param crop_coordinates: tuple: Crop coordinates for the images.
    :param dicom_type: DicomTypes: Type of DICOM file.
    :param pair_key: str: Key for the file pair.
    :param pair: dict: Dictionary containing the file pair.
    :param data_split: tuple: Data split percentages.
    :param color_changes: list: List of colour changes.
    :param file_pair_kwargs: dict: Keyword arguments for the file pair.
    :param save_func: function: Function to save the image and label pair.
    :param single_image_process: bool: Process a single image.

    :return: None
    """
    image_dir, label_dir = decide_data_split(output_dir, *data_split)

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
):
    """
    Convert a dataset of DICOM and NIfTI files.

    :param input_dir: str: Path to the input directory.
    :param output_dir: str: Path to the output directory.
    :param processes: int: Number of processes to use.
    :param crop_coordinates: tuple: Crop coordinates for the images.
    :param dicom_type: DicomTypes: Type of DICOM file.
    :param data_split: tuple: Data split percentages.
    :param color_changes: list: List of colour changes.
    :param file_pair_kwargs: dict: Keyword arguments for the file pair.
    :param save_func: function: Function to save the image and label pair.\
    :param single_image_process: bool: Process a single image.

    :return: None
    """

    file_pairs = defaultdict(lambda: {"dcm": None, "nii": None})

    for file in os.listdir(input_dir):
        if file.endswith(".dcm") or file.endswith(".nii.gz"):
            key = file.split(".")[0]
            if file.endswith(".dcm"):
                file_pairs[key]["dcm"] = file
            elif file.endswith(".nii.gz"):
                file_pairs[key]["nii"] = file

    pairs_to_process = [
        (pair_key, pair) for pair_key, pair in file_pairs.items()
    ]

    with Pool(processes=processes) as pool:
        pool.starmap(
            _process_file_pair,
            [
                (
                    input_dir,
                    output_dir,
                    crop_coordinates,
                    dicom_type,
                    pair_key,
                    pair,
                    data_split,
                    color_changes,
                    file_pair_kwargs,
                    save_func,
                    single_image_process,
                )
                for pair_key, pair in pairs_to_process
            ],
        )


def decide_data_split(
    dataset_dir: str, percent_train: float = 0.3, percent_val: float = 0.4
):
    """
    function to decide the split of the data

    :param dataset_dir: str: path to the dataset directory
    :param percent_train: float: percentage of data to be used for training
    :param percent_val: float: percentage of data to be used for validation

    :return: tuple: image_dir, label_dir
    """

    random = np.random.rand()

    if random < percent_train:
        image_dir = os.path.join(dataset_dir, "images/train")
        label_dir = os.path.join(dataset_dir, "labels/train")
    elif random < percent_val:
        image_dir = os.path.join(dataset_dir, "images/val")
        label_dir = os.path.join(dataset_dir, "labels/val")
    else:
        image_dir = os.path.join(dataset_dir, "images/test")
        label_dir = os.path.join(dataset_dir, "labels/test")

    return image_dir, label_dir
