from PIL import Image

from radstract.data.multimodal import remove_black_frames

ALL_BLACK = Image.new("RGB", (100, 100), (0, 0, 0))

LABELLED_IMAGE = Image.new("RGB", (100, 100), (255, 255, 255))
NON_LABELLED_IMAGE = Image.new("RGB", (100, 100), (0, 0, 0))


def test_remove_black_frames():
    dicom_list = [ALL_BLACK, NON_LABELLED_IMAGE]
    nifti_list = [ALL_BLACK, LABELLED_IMAGE]

    dicom_list, nifti_list = remove_black_frames(dicom_list, nifti_list)

    assert len(dicom_list) == 1
    assert len(nifti_list) == 1
    assert dicom_list[0] == NON_LABELLED_IMAGE
    assert nifti_list[0] == LABELLED_IMAGE
