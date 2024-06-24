import nibabel as nib
import numpy as np
from PIL import Image

from radstract.data.nifti import (
    NIFTI_Types,
    convert_images_to_nifti_labels,
    convert_nifti_to_image_labels,
)


def test_convert_nifti_to_image_labels_with_mock_data(nii_test_data):
    us_nii, us_labeL_image, idx = nii_test_data
    images, _ = convert_nifti_to_image_labels(us_nii)

    label_image = Image.open(us_labeL_image)

    assert all(
        isinstance(img, Image.Image) for img in images
    ), "All outputs should be PIL images"
    assert np.array_equal(
        np.array(images[idx]), np.array(label_image)
    ), "Image data should match the label image"


def test_convert_nifti_to_image_labels_with_compression(
    nii_test_data,
):
    us_nii, us_labeL_image, idx = nii_test_data

    images, _ = convert_nifti_to_image_labels(us_nii, compress_factor=2)

    label_image = Image.open(us_labeL_image)

    assert (
        abs(images[0].size[0] - ((label_image.size[0] // 2) + 1)) <= 1
        and abs(images[0].size[1] - (label_image.size[1] // 2)) <= 1
    ), "Image dimensions should be halved with a tolerance of +/- 1"


def test_convert_images_to_nifti_labels_with_mock_data(nii_test_data):
    us_nii, us_labeL_image, idx = nii_test_data

    image_list = [Image.open(us_labeL_image)]

    nifti = convert_images_to_nifti_labels(image_list)

    assert isinstance(
        nifti.image, nib.Nifti1Image
    ), "Should return a NIFTI image"
    assert nifti.image.shape[:-1] == (
        Image.open(us_labeL_image).size
    ), "NIFTI dimensions should match input images"
    assert (
        nifti.type == NIFTI_Types.NIBABEL
    ), "NIFTI type should be set correctly"
