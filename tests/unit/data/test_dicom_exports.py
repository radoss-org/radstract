import tempfile

import numpy as np
import pydicom
import pytest
from PIL import Image
from pydicom.dataset import FileMetaDataset

from radstract.data.dicom.exports import (
    PlaceHolderTag,
    add_anon_tags,
    add_tags,
    convert_images_to_dicom,
    create_empty_dicom,
)
from radstract.data.dicom.utils import DicomTypes


@pytest.mark.filterwarnings("ignore: Invalid value for VR UI:")
def test_add_anon_tags():
    dicom = pydicom.Dataset()
    keyint = 12345
    dicom = add_anon_tags(dicom, keyint)
    assert dicom.SeriesInstanceUID is not None
    assert dicom.SOPInstanceUID is not None
    assert dicom.StudyInstanceUID is not None
    assert dicom.SeriesNumber == keyint
    assert dicom.PatientID == f"radstract-{keyint}"
    assert dicom.StudyID == f"radstract-{keyint}"


@pytest.mark.filterwarnings("ignore: Invalid value for VR UI:")
def test_create_empty_dicom_default():
    dicom = create_empty_dicom()
    assert dicom.SeriesNumber == PlaceHolderTag.UseOldTagInt
    assert dicom.SeriesInstanceUID == PlaceHolderTag.UseOldTagUID
    assert dicom.SOPInstanceUID == PlaceHolderTag.UseOldTagUID
    assert dicom.StudyInstanceUID == PlaceHolderTag.UseOldTagUID
    assert dicom.PatientID == PlaceHolderTag.UseOldTagStr
    assert dicom.PatientName == PlaceHolderTag.UseOldTagStr
    assert dicom.StudyID == PlaceHolderTag.UseOldTagStr


@pytest.mark.filterwarnings("ignore: Invalid value for VR UI:")
def test_create_empty_dicom_series():
    dicom = create_empty_dicom(DicomTypes.SERIES)
    assert dicom.SeriesNumber == PlaceHolderTag.UseOldTagInt


@pytest.mark.filterwarnings("ignore: Invalid value for VR UI:")
def test_create_empty_dicom_series_anonymized():
    dicom = create_empty_dicom(DicomTypes.SERIES_ANONYMIZED, keyint=54321)
    assert dicom.SeriesInstanceUID is not None
    assert dicom.SOPInstanceUID is not None
    assert dicom.StudyInstanceUID is not None


def mock_empty_dicom(dicom):
    dicom.file_meta = FileMetaDataset()

    dicom.SamplesPerPixel = 3
    dicom.PhotometricInterpretation = "RGB"
    dicom.PixelRepresentation = 0
    dicom.BitsStored = 8
    dicom.BitsAllocated = 8
    dicom.HighBit = 7

    # Ultrasound Image Storage
    # https://dicom.nema.org/dicom/2013/output/chtml/part04/sect_i.4.html
    dicom.SOPClassUID = "1.2.840.10008.5.1.4.1.1.6.1"

    dicom.SeriesInstanceUID = pydicom.uid.generate_uid()
    dicom.SOPInstanceUID = pydicom.uid.generate_uid()
    dicom.StudyInstanceUID = pydicom.uid.generate_uid()

    return dicom


@pytest.mark.filterwarnings("ignore:Tag Patient's Name")
def test_add_tags(ultrasound_dcm):
    old_dicom = pydicom.dcmread(ultrasound_dcm)
    new_dicom = pydicom.Dataset()
    new_dicom.SeriesNumber = PlaceHolderTag.UseOldTagInt

    # make the above more consize
    old_tags_str = [
        "PatientID",
        "PatientName",
        "StudyID",
    ]

    old_tags_uid = [
        "SeriesInstanceUID",
        "SOPInstanceUID",
        "StudyInstanceUID",
    ]

    for tag in old_tags_str:
        setattr(new_dicom, tag, PlaceHolderTag.UseOldTagStr)

    for tag in old_tags_uid:
        setattr(new_dicom, tag, PlaceHolderTag.UseOldTagUID)

    new_dicom = add_tags(new_dicom, old_dicom)

    assert new_dicom.SOPInstanceUID == old_dicom.SOPInstanceUID
    assert new_dicom.StudyInstanceUID == old_dicom.StudyInstanceUID
    assert new_dicom.PatientID == old_dicom.PatientID
    assert new_dicom.StudyID == old_dicom.StudyID


# NOTE(2024-04-20 Sharpz7) This filter can be made more specific in the
# future by remaking the example dicoms
@pytest.mark.filterwarnings("ignore:Tag")
def test_convert_images_to_dicom(ultrasound_label_slice0):
    tags = pydicom.Dataset()
    tags = mock_empty_dicom(tags)

    test_image = Image.open(ultrasound_label_slice0).convert("RGB")
    images = [test_image]

    new_dicom = convert_images_to_dicom(images, tags)

    assert isinstance(new_dicom, pydicom.Dataset)
    assert new_dicom.NumberOfFrames == len(images)
    assert new_dicom.Rows == test_image.height
    assert new_dicom.Columns == test_image.width
    # assert that FileMetaDataset is present
    assert isinstance(new_dicom.file_meta, FileMetaDataset)

    # Save the new DICOM to a temporary file and compare the pixel data
    with tempfile.NamedTemporaryFile(suffix=".dcm") as temp_dicom:
        new_dicom.save_as(temp_dicom.name)
        loaded_dicom = pydicom.dcmread(temp_dicom.name)
        # NOTE(2024-04-20 Sharpz7) Slight difference in
        # pixel values due to conversion
        assert np.allclose(
            loaded_dicom.pixel_array, np.array(test_image), atol=3
        )
