"""
Radstract supports compose-based filtering operations on images. The `reduce_noise` function
takes an image and a list of filters to apply to the image. The filters are applied in the order.

Note that custom filters can be applied by using the LambdaFilter class.
"""

import cv2
import pydicom

from radstract.data.dicom import convert_dicom_to_images
from radstract.data.images import NoiseReductionFilter, reduce_noise
from radstract.testdata import Cases, download_case

dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

dcm = pydicom.dcmread(dcm_file)
dicom_images = convert_dicom_to_images(dcm)

img = dicom_images[0]


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

test.save("debug/noise-reduction.png")
