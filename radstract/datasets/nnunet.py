"""
NN-UNet utility functions
"""

import os
import random
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import SimpleITK as sitk

from radstract.data.dicom import DicomTypes
from radstract.data.nifti import NIFTI, convert_images_to_nifti_labels

from .utils import DataSplit, convert_dcm_nii_dataset


def nnunet_decide_split(
    root_output_dir: str,
    image_dir: str,
    label_dir: str,
) -> Tuple[str, str]:
    """
    Decide the split for the nnU-Net dataset.

    :param root_output_dir: str: Root output directory.
    :param image_dir: str: Image directory.
    :param label_dir: str: Label directory.

    :return: Tuple containing the image NIFTI and label NIFTI directories.
    """

    # get the last part of the image_dir
    split_dir = image_dir.split("/")[-1]

    if split_dir == "val":
        raise ValueError("nnUNet does not have validation data")

    mapping = {
        "train": "imagesTr",
        "test": "imagesTs",
    }

    split_dir = mapping[split_dir]

    nii_dir = os.path.join(root_output_dir, split_dir)
    nii_label_dir = os.path.join(root_output_dir, "labelsTr")

    return nii_dir, nii_label_dir


def save_nunnet(
    images: List[str],
    image_labels: List[str],
    image_dir: str,
    label_dir: str,
    file_name: str,
    file_pair_kwargs: Optional[dict] = None,
) -> None:
    # remove everything from dir after images/
    root_output_dir = image_dir.split("images/")[0]

    nii_dir, nii_label_dir = nnunet_decide_split(
        root_output_dir, image_dir, label_dir
    )

    nifti_image = NIFTI(sitk.GetImageFromArray(np.array(images)))
    nifti_label = convert_images_to_nifti_labels(image_labels)

    nifti_image.save(os.path.join(nii_dir, f"{file_name}.nii.gz"))
    nifti_label.save(os.path.join(nii_label_dir, f"{file_name}.nii.gz"))


def convert_dataset_to_nnunet(
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
    for split in ["imagesTr", "imagesTs", "labelsTr"]:
        os.makedirs(os.path.join(output_dir, split), exist_ok=True)

    # Convert the dataset to a Huggingface DatasetDict
    convert_dcm_nii_dataset(
        input_dir,
        output_dir,
        processes=processes,
        crop_coordinates=crop_coordinates,
        dicom_type=dicom_type,
        data_split=data_split,
        color_changes=color_changes,
        file_pair_kwargs={},
        save_func=save_nunnet,
        single_image_process=False,
        datasplit_seed=datasplit_seed,
    )


def generate_nnunet_dataset_json(
    nnunet_dir_structure: dict,
    dataset_name: str,
    modalities: Dict[str, str],
    labels: Dict[str, str],
    description: str = "Dataset for nnU-Net model",
    reference: str = "Put your reference here",
    licence: str = "Dataset license",
    release: str = "1.0",
    tensorImageSize: str = "4D",
):
    """
    Generate dataset.json for nnU-Net configuration.

    :param nnunet_dir_structure: Dictionary containing the nnU-Net directory structure
    :param dataset_name: Name of the dataset
    :param modalities: Dictionary containing the modalities {"0": "MRI", "1": "CT", ...}
    :param labels: Dictionary containing the labels {"0": "Label1", "1": "Label2", ...}
    :param description: Description of the dataset
    :param reference: Reference for the dataset
    :param licence: Licence for the dataset
    :param release: Release version

    :return: Dictionary containing the dataset.json
    """

    json_dict = {
        "name": dataset_name,
        "description": description,
        "tensorImageSize": tensorImageSize,
        "reference": reference,
        "licence": licence,
        "release": release,
        "modality": modalities,
        "labels": labels,
        "numTest": len(os.listdir(nnunet_dir_structure["imagesTs"])),
        "numTraining": len(os.listdir(nnunet_dir_structure["imagesTr"])),
        "training": [
            {
                "image": f"./imagesTr/{i}",
                "label": f"./labelsTr/{i}",
            }
            for i in sorted(os.listdir(nnunet_dir_structure["imagesTr"]))
        ],
        "test": [
            {
                "image": f"./imagesTs/{i}",
                "label": f"./labelsTr/{i}",
            }
            for i in sorted(os.listdir(nnunet_dir_structure["imagesTs"]))
        ],
    }

    # Update numTest according to the actual test cases
    json_dict["numTest"] = len(os.listdir(nnunet_dir_structure["imagesTs"]))

    return json_dict


def build_nnunet_dir_structure(input_dir):
    """
    Build the nnunet_dir_structure dictionary based on the input directory.

    :param input_dir: Path to the input directory containing the nnU-Net dataset
    :return: Dictionary containing the nnU-Net directory structure
    """
    nnunet_dir_structure = {
        "imagesTr": os.path.join(input_dir, "imagesTr"),
        "imagesTs": os.path.join(input_dir, "imagesTs"),
        "labelsTr": os.path.join(input_dir, "labelsTr"),
    }

    # Check if the required directories exist
    for dir_path in nnunet_dir_structure.values():
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory not found: {dir_path}")

    return nnunet_dir_structure
