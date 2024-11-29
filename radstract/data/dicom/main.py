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

    trigger = False
    data = old_dicom.pixel_array

    if dicom_type == DicomTypes.SINGLE:
        data = [old_dicom.pixel_array]

    for frame in data:
        # See https://github.com/pydicom/pydicom/issues/533
        if not trigger:
            trigger = True

        image = Image.fromarray(frame)

        image = crop_and_resize(image, crop_coordinates, compress_factor)

        image = reduce_noise(image, noise_filters)

        images.append(image)

    return images
