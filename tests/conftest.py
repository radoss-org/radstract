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

import logging
import os

import pytest

from radstract.testdata import Cases, download_case

# check if test-data exists, otherwise print a message
if not os.path.exists("tests/test_data"):
    logging.error("No test data found. Please run `poe testgen`")
    exit(1)

dcm_us, seg_file = download_case(Cases.ULTRASOUND_DICOM)
dcm_xray = download_case(Cases.XRAY_DCM)
us_nii, us_labeL_image = download_case(Cases.ULTRAOUND_NIFTI_TEST)


@pytest.fixture
def ultrasound_dcm():
    return dcm_us


@pytest.fixture
def ultrasound_nifti_labels():
    return seg_file


@pytest.fixture
def xray_dcm():
    return dcm_xray


@pytest.fixture
def nii_test_data():
    return us_nii, us_labeL_image, 14


@pytest.fixture
def dataset_dir():
    return "./tests/test_data/dataset"


@pytest.fixture
def ultrasound_label_slice0():
    return "tests/test_data/171551_slice0.png"


@pytest.fixture
def ultrasound_label_slice0_noise():
    return "tests/test_data/171551_slice0_noise.png"


@pytest.fixture
def model_3d():
    return "tests/test_data/171551.ply"


@pytest.fixture
def dicom_nifti_data():
    dcm, nii = download_case(Cases.ULTRASOUND_DICOM_NIFTI_TEST)
    return dcm, nii
