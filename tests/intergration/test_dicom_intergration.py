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
