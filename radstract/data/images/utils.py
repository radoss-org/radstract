"""
Crop and Resize Utility Functions for Images.

Used by the DICOM and NIFTI data importers.
"""

from typing import Tuple

import numpy as np
from PIL import Image


def crop_and_resize(
    img: Image.Image,
    crop_coordinates: Tuple[int, int, int, int] = None,
    compress_factor: int = 1,
    for_label: bool = False,
):
    """
    Crop and resize a Image.

    :param image: PIL Image object.
    :param crop_coordinates: Tuple (x, y, width, height) for the crop area.
    :param compress_factor: Factor to compress the cropped images.
    :param for_label: Boolean to indicate if the image is a label.

    :return: cropped and resized PIL image.
    """

    if crop_coordinates:
        x, y, width, height = crop_coordinates

        # Calculate new dimensions after compression
        new_width, new_height = int(width / compress_factor), int(
            height / compress_factor
        )

        # Crop image
        cropped_image = img.crop((x, y, x + width, y + height))

    else:
        cropped_image = img
        new_width, new_height = img.size

    # To Handle
    # https://stackoverflow.com/questions/31300865/srgb-aware-image-resize-in-pillow/31359054
    if for_label:
        # Initialize compressed image
        resized_image = np.zeros((new_height, new_width, 3))

        image_array = np.array(cropped_image)

        # Apply compression
        resized_image = image_array[::compress_factor, ::compress_factor]

        # Convert to PIL image
        resized_image = Image.fromarray(resized_image, "RGB")

    else:
        resized_image = cropped_image.resize((new_width, new_height))

    return resized_image
