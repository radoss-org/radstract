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
