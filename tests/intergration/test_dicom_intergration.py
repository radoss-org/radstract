import tempfile

import pydicom
import pytest

from radstract.data.dicom import DicomTypes, convert_dicom_to_images
from radstract.data.dicom.exports import (
    convert_images_to_dicom,
    create_empty_dicom,
)


# NOTE(2024-04-20 Sharpz7) This filter can be made more specific in the
# future by remaking the example dicoms
@pytest.mark.filterwarnings("ignore:Tag")
def test_convert_dicom_series(ultrasound_dcm):
    ds = pydicom.dcmread(ultrasound_dcm)

    important_tags = create_empty_dicom(dicom_type=DicomTypes.SERIES)
    important_tags.SeriesDescription = "Created with Radstract"
    important_tags.PatientName = "Test^Test"

    # check pixel_array shape
    images = convert_dicom_to_images(ds, dicom_type=DicomTypes.SERIES)

    new_ds = convert_images_to_dicom(images, important_tags, ds)

    with tempfile.TemporaryDirectory() as tmpdirname:
        new_ds.save_as(f"{tmpdirname}/test.dcm", write_like_original=False)

        test = pydicom.dcmread(f"{tmpdirname}/test.dcm")
        assert test.pixel_array.shape == (
            len(images),
            images[0].size[1],
            images[0].size[0],
            3,
        )
