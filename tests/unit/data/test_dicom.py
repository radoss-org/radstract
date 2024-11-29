import numpy as np
import pydicom
from PIL import Image

from radstract.data.dicom import convert_dicom_to_images


def test_convert_dicom_to_images(ultrasound_dcm, ultrasound_label_slice0):
    old_dicom = pydicom.dcmread(ultrasound_dcm)

    images = convert_dicom_to_images(old_dicom)

    assert isinstance(images, list)
    assert len(images) > 0
    assert all(isinstance(img, Image.Image) for img in images)

    # Compare the first image with the test image
    test_image = Image.open(ultrasound_label_slice0).convert("RGB")

    # NOTE(2024-04-20 Sharpz7) Slight difference in pixel values due to conversion
    assert np.allclose(np.array(images[0]), np.array(test_image), atol=3)
