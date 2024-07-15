"""
Handles the conversion of DICOM datasets to images.

Example: https://github.com/radoss-org/Radstract/tree/main/examples/data/dicom_import.py
"""

import warnings
from typing import List, Tuple

import pydicom
from PIL import Image

from radstract.data.colors import get_unique_colours
from radstract.data.dicom.utils import DicomTypes
from radstract.data.images import (
    NoiseReductionFilter,
    crop_and_resize,
    reduce_noise,
)


class PhotometricInterpretation:
    YBR_FULL_422 = "YBR_FULL_422"
    RGB = "RGB"


def convert_dicom_img_to_rgb(
    image: Image.Image, photometric_interpretation: PhotometricInterpretation
):
    """
    Convert an image from any color space to RGB using NumPy.

    :param image: NumPy array representing an image.
    :param photometric_interpretation: The photometric interpretation of the image.

    :return: NumPy array representing the image in RGB color space.

    :raises NotImplementedError: If the photometric interpretation is not supported.
    """

    if photometric_interpretation == PhotometricInterpretation.RGB:
        rgb = Image.fromarray(image, mode="RGB")

        # This means that the image has been processed wrong,
        # and we should try to convert it to YCbCr and then to RGB
        if len(get_unique_colours(rgb)) == 0:
            # Log a warning
            warnings.warn(
                "Image is in RGB but has no unique colours. "
                "Attempting known fix..."
            )
            image = Image.fromarray(image, mode="YCbCr")
            rgb = image.convert("RGB")

    elif photometric_interpretation in [
        PhotometricInterpretation.YBR_FULL_422,
        PhotometricInterpretation.YBR_FULL,
    ]:
        image = Image.fromarray(image, mode="YCbCr")
        rgb = image.convert("RGB")

    # All PhotometricInterpretations that we know can be converted automatically
    elif photometric_interpretation in [PhotometricInterpretation.MONOCHROME2]:
        image = Image.fromarray(image)
        rgb = image.convert("RGB")

    else:
        # warn that the image is not in garanteed supported format, and
        # the default conversion will be used
        warnings.warn(
            f"Image is in {photometric_interpretation}. "
            "Attempting default conversion to RGB..."
        )
        image = Image.fromarray(image)
        rgb = image.convert("RGB")

    return rgb


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

        image = convert_dicom_img_to_rgb(
            frame, old_dicom.PhotometricInterpretation
        )

        image = crop_and_resize(image, crop_coordinates, compress_factor)

        image = reduce_noise(image, noise_filters)

        images.append(image)

    return images
