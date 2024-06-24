import cv2
import numpy as np
from PIL import Image

from radstract.data.images import (
    NoiseReductionFilter,
    crop_and_resize,
    reduce_noise,
)

ALL_BLACK = Image.new("RGB", (100, 100), (0, 0, 0))
CROPPED_AND_RESIZED_ALL_BLACK = Image.new("RGB", (50, 50), (0, 0, 0))


def test_crop_and_resize():
    assert (
        crop_and_resize(ALL_BLACK, crop_coordinates=(0, 0, 50, 50))
        == CROPPED_AND_RESIZED_ALL_BLACK
    )
    assert crop_and_resize(ALL_BLACK, compress_factor=2) == ALL_BLACK


def test_reduce_noise(ultrasound_label_slice0, ultrasound_label_slice0_noise):
    img = Image.open(ultrasound_label_slice0)
    noise_reduced_img = Image.open(ultrasound_label_slice0_noise)

    def custom_filter(image):
        # Apply custom filtering operations to the image
        # For example, let's apply a simple threshold
        _, filtered_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
        return filtered_image

    test = reduce_noise(
        img,
        [
            NoiseReductionFilter.MEDIAN_FILTER(size=5),
            NoiseReductionFilter.GAUSSIAN_BLUR(kernel_size=(5, 5)),
            NoiseReductionFilter.BILATERAL_FILTER(
                diameter=9, sigma_color=75, sigma_space=75
            ),
            NoiseReductionFilter.LAMBDA_FILTER(func=custom_filter),
        ],
    )

    assert np.array_equal(np.array(test), np.array(noise_reduced_img))
