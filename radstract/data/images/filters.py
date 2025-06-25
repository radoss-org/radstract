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
Compose System for handling image filters.

Examples: https://github.com/radoss-org/Radstract/tree/main/examples/data/filters.py
"""

import warnings
from typing import List

import cv2
import numpy as np
from PIL import Image


class FilterParameters:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def filters(func):
    def wrapper(*args, **kwargs):
        filter_params = func(*args, **kwargs)
        filter_params.type = func.__name__
        return filter_params

    wrapper.type = func.__name__
    return wrapper


class NoiseReductionFilter:
    @filters
    def MEDIAN_FILTER(size=5):
        return FilterParameters(size=size)

    @filters
    def GAUSSIAN_BLUR(kernel_size=(5, 5)):
        return FilterParameters(kernel_size=kernel_size)

    @filters
    def BILATERAL_FILTER(diameter=9, sigma_color=75, sigma_space=75):
        return FilterParameters(
            diameter=diameter,
            sigma_color=sigma_color,
            sigma_space=sigma_space,
        )

    @filters
    def LAMBDA_FILTER(func):
        return FilterParameters(func=func)

    DEFAULT = []


def reduce_noise(
    image: Image.Image, filters_compose: List[NoiseReductionFilter] = []
) -> Image.Image:
    """
    Apply noise reduction techniques to an image.

    Note that a RGB2BGR conversion is done before applying the filters.

    :param image: Pillow image to be processed.
    :param filters_compose: List of NoiseReductionFilter
           enums representing the filters to apply.

    :return: Processed Pillow image.
    """

    # Convert Pillow image to OpenCV format
    image_cv = np.array(image)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)

    if len(filters_compose) == 0:
        return image

    for fil_func in filters_compose:
        if fil_func.type == NoiseReductionFilter.MEDIAN_FILTER.type:
            image_cv = cv2.medianBlur(image_cv, fil_func.size)
        elif fil_func.type == NoiseReductionFilter.GAUSSIAN_BLUR.type:
            image_cv = cv2.GaussianBlur(image_cv, fil_func.kernel_size, 0)
        elif fil_func.type == NoiseReductionFilter.BILATERAL_FILTER.type:
            diameter, sigma_color, sigma_space = (
                fil_func.diameter,
                fil_func.sigma_color,
                fil_func.sigma_space,
            )
            image_cv = cv2.bilateralFilter(
                image_cv,
                diameter,
                sigma_color,
                sigma_space,
            )
        elif fil_func.type == NoiseReductionFilter.LAMBDA_FILTER.type:
            image_cv = fil_func.func(image_cv)
        else:
            warnings.warn(f"Unknown filter type: {fil_func.type}")

    # Convert back to Pillow format
    processed_image = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))

    return processed_image
