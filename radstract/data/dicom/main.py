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
Handles the conversion of DICOM datasets to images.

Example: https://github.com/radoss-org/Radstract/tree/main/examples/data/dicom_import.py
"""

from typing import List, Tuple

import pydicom
from PIL import Image

from radstract.data.dicom.utils import DicomTypes
from radstract.data.images import (
    NoiseReductionFilter,
    crop_and_resize,
    reduce_noise,
)


class PhotometricInterpretation:
    YBR_FULL_422 = "YBR_FULL_422"
    YBR_FULL = "YBR_FULL"
    RGB = "RGB"
    MONOCHROME2 = "MONOCHROME2"


def convert_dicom_to_images(
    old_dicom: pydicom.Dataset,
    crop_coordinates: Tuple[int, int, int, int] = None,
    compress_factor: int = 1,
    dicom_type: str = DicomTypes.DEFAULT,
    noise_filters: List[NoiseReductionFilter] = NoiseReductionFilter.DEFAULT,
) -> Image.Image:
    """
    Converts a DICOM dataset to a new format, transferring specified tags,
    with options to crop and resize the image.

    :param old_dicom: pydicom Dataset object.
    :param crop_coordinates: Optional tuple (x, y, width, height) for cropping.
    :param compress_factor: Optional scalar for resizing.
    :param dicom_type: The DICOM Type from the DicomTypes Enum.
    :param noise_filters: Optional list of NoiseReductionFilter enums.

    :return: New DICOM dataset with specified tags transferred, and image
    cropped and resized if specified.

    :raises NotImplementedError: If the DICOM type is not supported.
    """

    if dicom_type not in DicomTypes.ALL_TYPES:
        raise NotImplementedError(
            f"Dicom type {dicom_type} not implemented yet. Please choose from {DicomTypes.ALL_TYPES}"
        )

    images = []

    data = old_dicom.pixel_array

    if dicom_type == DicomTypes.SINGLE:
        data = [old_dicom.pixel_array]

    for frame in data:
        image = Image.fromarray(frame)
        image = image.convert("RGB")

        image = crop_and_resize(image, crop_coordinates, compress_factor)

        image = reduce_noise(image, noise_filters)

        images.append(image)

    return images
