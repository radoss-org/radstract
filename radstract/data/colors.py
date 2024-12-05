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
All functions for colour manipulation and conversion within images

Examples:
- https://github.com/radoss-org/Radstract/tree/main/examples/data/colors.py
"""

import time
from typing import Tuple

import numpy as np
from PIL import Image


class LabelColours:
    """
    Class to hold the label colours.

    Note these are labelled in the same order as ITK Snap.
    The LABELS attribute now returns a generator
    that yields predefined colors first and then indefinitely
    generates new unique colors.
    """

    # Predefined colors
    LABEL1 = (255, 0, 0)  # Red
    LABEL2 = (0, 255, 0)  # Green
    LABEL3 = (0, 0, 255)  # Blue
    LABEL4 = (255, 255, 0)  # Yellow
    LABEL5 = (0, 128, 128)  # Teal
    LABEL6 = (128, 0, 128)  # Purple
    BLACK = (0, 0, 0)  # Black
    used_labels = [LABEL1, LABEL2, LABEL3, LABEL4, LABEL5, LABEL6]

    random = np.random.default_rng(42)

    @classmethod
    def _generate_new_color(self):
        """
        Generates a new color ensuring it's not similar
        to predefined or previously generated colors.
        """

        while True:
            new_color = (
                self.random.integers(0, 255),
                self.random.integers(0, 255),
                self.random.integers(0, 255),
            )
            if not self._is_similar(new_color):
                self.used_labels.append(new_color)
                return new_color

    @classmethod
    def _is_similar(self, new_color):
        """Check if the new color is too close to any used colors."""
        return any(
            self._color_distance(new_color, old_color) < 100
            for old_color in self.used_labels
        )

    @classmethod
    def _color_distance(self, c1, c2):
        """Calculate the Euclidean distance between two colors."""
        return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

    @classmethod
    def _label_colour_gen(self):
        """
        Generator that yields all predefined
        colors and then new unique colors indefinitely.
        """
        timeout = 5
        start_time = time.time()

        for color in self.used_labels:
            yield color

        while time.time() - start_time < timeout:
            yield self._generate_new_color()

    @classmethod
    def get_color_from_index(cls, index: int) -> Tuple[int, int, int]:
        """
        Get the colour from the index.

        :param index: The index to get the colour for.

        :return: The colour as a tuple.
        """

        if index == 0:
            return cls.BLACK

        # Use label_colour_gen to get the color
        for i, color in enumerate(cls._label_colour_gen()):
            if i == (index - 1):
                return color

    @classmethod
    def get_colour_key(
        cls,
        colour: Tuple[int, int, int],
        background: Tuple[int, int, int] = BLACK,
    ) -> int:
        """
        Get the colour key for the given colour.

        :param colour: The colour to get the key for.
        :param background: The background colour.

        :return: The colour key.
        """

        # convert away from numpy array
        colour = tuple(colour)

        if colour == background:
            return 0

        for i, color in enumerate(cls._label_colour_gen()):
            if color == colour:
                return i + 1

        return None


def get_unique_colours(
    img: Image.Image = None, array: np.ndarray = None
) -> Tuple[Tuple[int, int, int]]:
    """
    Get the unique colours in an image.

    :param img: Pillow image to be processed.
    :param array: Numpy array to be processed.

    :return: List of unique colours in the image.

    :raises ValueError: If both img and array are provided.
    """

    if img is not None and array is not None:
        raise ValueError("Only one of img or array must be provided.")

    elif img is not None:
        unique_colors = img.convert("RGB").getcolors()

    elif array is not None:
        unique_colors = Image.fromarray(array).convert("RGB").getcolors()

    else:
        raise ValueError("Either img or array must be provided.")

    if unique_colors is None:
        return ()

    # since these return count, colour, only return the 2nd element of each tuple
    unique_colors = tuple([colour for _, colour in unique_colors])
    return unique_colors


def change_color(
    img: Image.Image,
    old_color: Tuple[int, int, int],
    new_color: Tuple[int, int, int],
) -> Image.Image:
    """
    Change the target color to the replacement color in the image.

    :param img: The image to change the color in.
    :param old_color: The target color to change.
    :param new_color: The replacement color.

    :return: The image with the color changed.
    """

    data = np.array(img)
    mask = np.all(data == old_color, axis=-1)

    data[mask] = new_color

    return Image.fromarray(data)


# Custom function to create a color map
def convert_labels_to_image(slice_data: np.ndarray) -> np.ndarray:
    """
    Applies a colour mapping of segmentaitions to colours.

    :param slice_data: The slice data to apply the colour map to.

    :return: The colour mapped data.
    """

    color_mapped_data = np.zeros((slice_data.shape[0], slice_data.shape[1], 3))

    for mask in np.sort(np.unique(slice_data)):
        if mask != 0:
            color_mapped_data[
                slice_data == mask
            ] = LabelColours.get_color_from_index(int(mask))

    return color_mapped_data


def fast_check_all_black(img: Image) -> bool:
    """
    Check if the given image is all black.

    :param img: The image to check

    :return: True if the image is all black, False otherwise.
    """

    result = np.array(img).sum()
    if result == 0:
        return True
    return False
