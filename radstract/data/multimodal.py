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

"""
For things involving both DICOM and NIFTIs, like:

- Removing black frames from both DICOM and NIFTI-Label lists
- Converting DICOM to NIFTI

Examples:
- https://github.com/radoss-org/Radstract/tree/main/examples/data_conversions.py
"""

import logging
import warnings
from typing import List, Optional, Tuple

import numpy as np
import pydicom
import SimpleITK as sitk
from PIL import Image

from radstract.data.colors import fast_check_all_black
from radstract.data.dicom import (
    DicomTypes,
    NoiseReductionFilter,
    convert_dicom_to_images,
)
from radstract.data.nifti import NIFTI


def remove_black_frames(
    dicom_list: List[Image.Image], nifti_label_list: List[Image.Image]
) -> Tuple[List[Image.Image], List[Image.Image]]:
    """
    Remove black frames from both dicom and nifti lists based on nifti images.

    :param dicom_list: The list of DICOM-based image files
    :param nifti_label_list: The list of NIfTI-label based image files

    :return: The filtered DICOM and NIfTI lists.
    """

    if len(dicom_list) != len(nifti_label_list):
        warnings.warn(
            "DICOM and NIFTI lists are of different lengths. Check the data."
        )
        return dicom_list, nifti_label_list

    # Create copies to avoid modifying original lists
    dicom_list_copy = dicom_list.copy()
    nifti_list_copy = nifti_label_list.copy()

    saved_frames = []

    # Filter out black frames
    for index in reversed(range(len(nifti_list_copy))):
        if fast_check_all_black(nifti_list_copy[index]):
            del dicom_list_copy[index]
            del nifti_list_copy[index]
        else:
            saved_frames.append(index)

    # Log which frames were saved
    logging.info(f"Saved frames: {saved_frames}")
    return dicom_list_copy, nifti_list_copy


def convert_dicom_to_nifti(
    dicom: pydicom.Dataset,
    crop_coordinates: Optional[Tuple[int, int, int, int]] = None,
    compress_factor: Optional[int] = 1,
    dicom_type: Optional[DicomTypes] = DicomTypes.DEFAULT,
    noise_filters: Optional[
        NoiseReductionFilter
    ] = NoiseReductionFilter.DEFAULT,
) -> NIFTI:
    """
    Convert a DICOM file to NIfTI format using SimpleITK.

    Args:
    dicom: The DICOM Object.
    crop_coordinates: Crop coordinates for the conversion.
    compress_factor: Compression factor for the conversion.
    dicom_type: The type of DICOM file.
    noise_filters: The noise filters to apply.

    Returns:
    The converted NIfTI data.
    """

    dicom_images = convert_dicom_to_images(
        dicom,
        crop_coordinates=crop_coordinates,
        compress_factor=compress_factor,
        dicom_type=dicom_type,
        noise_filters=noise_filters,
    )

    image = sitk.GetImageFromArray(np.array(dicom_images))

    return NIFTI(image)
