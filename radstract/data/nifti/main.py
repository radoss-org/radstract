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
Handles all the NIFTI functions for Radstract

Examples:
- https://github.com/radoss-org/Radstract/tree/main/examples/data/nifti_creation.py
- https://github.com/radoss-org/Radstract/tree/main/examples/data/nifti_import.py
"""

from typing import List, Tuple, Union

import nibabel as nib
import numpy as np
import SimpleITK as sitk
from nibabel.nifti1 import Nifti1Image
from PIL import Image

from radstract.data.colors import (
    LabelColours,
    convert_labels_to_image,
    get_unique_colours,
)
from radstract.data.images import crop_and_resize


class NIFTI_Types:
    """
    Class to hold the NIfTI types.
    """

    SITK = "sitk"
    NIBABEL = "nibabel"


class NIFTI:
    """
    Using sitk because nibabel needs the correct affine matrix to be set.
    That has not been figured out yet.
    """

    def __init__(self, image, type=NIFTI_Types.SITK):
        self.image = image
        self.type = type

    def save(self, out_path: str, useCompression: bool = True) -> None:
        """
        Save the NIfTI image to a file.

        :param out_path: The output path to save the NIfTI file.
        :param useCompression: Whether to use compression or not.

        :return: None

        :raises ValueError: If the NIfTI type is unknown.
        """
        if self.type == NIFTI_Types.SITK:
            sitk.WriteImage(
                self.image, out_path, useCompression=useCompression
            )
        elif self.type == NIFTI_Types.NIBABEL:
            nib.save(self.image, out_path)

        else:
            raise ValueError(f"Unknown NIfTI type {self.type}")


# Function to process NIfTI files
def convert_nifti_to_image_labels(
    nii: Union[str, Nifti1Image],
    crop_coordinates: Tuple[int, int, int, int] = None,
    compress_factor: int = 1,
) -> Tuple[List[Image.Image], np.ndarray]:
    """
    Process a NIfTI file to extract each frame and convert to JPEG images
    with the label colours displayed.

    Currently assumes RAI Orientation, and uses ITK Snap conventions for
    the label colours.

    :param nii: Either a NIfTI file path or a NIfTI object.
    :param crop_coordinates: The crop coordinates for the images.
    :param compress_factor: The compression factor for the images.

    :return: A tuple of the list of JPEG images and the affine matrix.
    """

    if isinstance(nii, str):
        nii = nib.load(nii)

    data = nii.get_fdata()
    images = []

    for i in range(data.shape[2]):
        slice_data = data[:, :, i]
        slice_data = np.rot90(slice_data)  # rotate 90 degrees clockwise
        slice_data = np.flipud(slice_data)  # flip vertically

        color_mapped_slice = convert_labels_to_image(slice_data)

        img = Image.fromarray((color_mapped_slice).astype("uint8"), "RGB")

        # Apply crop and resize
        img = crop_and_resize(
            img, crop_coordinates, compress_factor, for_label=True
        )

        images.append(img)

    return images, nii.affine


def convert_images_to_nifti_labels(images: List[Image.Image]) -> NIFTI:
    """
    Convert a list of images to NIfTI format using SimpleITK.

    :param images: List of PIL images.

    :return: NIfTI object.
    """

    final_data = np.zeros(
        (images[0].height, images[0].width, len(images)), dtype=np.uint16
    )

    for i, image in enumerate(images):
        img_array = np.array(image, dtype=np.uint16)

        for unique_colour in get_unique_colours(img=image):
            # Find the coordinates of the pixels that match the unique colour.
            label_key = LabelColours.get_colour_key(unique_colour)
            mask = np.all(img_array == unique_colour, axis=2)
            final_data[:, :, i][mask] = label_key

    # Moving back to RAI orientation

    # rotate 90 degrees clockwise
    final_data = np.rot90(final_data)
    # flip vertically
    final_data = np.flipud(final_data)

    # RAI affine (apparently)
    # https://chat.openai.com/c/45d4627e-4b69-44fc-b68f-1d5ab90111dc
    affine = np.diag([-1, -1, 1, 1])

    image = nib.Nifti1Image(final_data, affine=affine)

    return NIFTI(image, type=NIFTI_Types.NIBABEL)


def convert_nifti_to_images(
    nii: Union[str, Nifti1Image],
    crop_coordinates: Tuple[int, int, int, int] = None,
    compress_factor: int = 1,
) -> Tuple[List[Image.Image], np.ndarray]:
    """
    Process a NIfTI file to extract each frame and convert to JPEG images.

    Currently assumes RAI Orientation.

    For label-based NIfTI files, use convert_nifti_to_image_labels.

    :param nii: Either a NIfTI file path or a NIfTI object.
    :param crop_coordinates: The crop coordinates for the images.
    :param compress_factor: The compression factor for the images.

    :return: The list of JPEG images.
    """

    if isinstance(nii, str):
        nii = nib.load(nii)

    data = nii.get_fdata()
    images = []

    for i in range(data.shape[2]):
        slice_data = data[:, :, i, :]
        # remove the 3rd dimension
        slice_data = np.squeeze(slice_data, axis=2)
        slice_data = np.rot90(slice_data)  # rotate 90 degrees clockwise
        slice_data = np.flipud(slice_data)  # flip vertically

        img = Image.fromarray((slice_data).astype("uint8"), "RGB")

        # Apply crop and resize
        img = crop_and_resize(
            img, crop_coordinates, compress_factor, for_label=True
        )

        images.append(img)

    return images, nii.affine
