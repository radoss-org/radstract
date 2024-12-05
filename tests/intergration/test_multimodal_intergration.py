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

import nibabel as nib
import numpy as np
import pydicom

from radstract.data.multimodal import convert_dicom_to_nifti
from radstract.data.nifti import convert_nifti_to_images


def test_convert_dicom_to_nifti(dicom_nifti_data):
    dcm_file, nii_file = dicom_nifti_data
    dcm = pydicom.dcmread(dcm_file)
    nifti = nib.load(nii_file)

    dcm_nifti = convert_dicom_to_nifti(dcm)
    # create a temp file to save the nifti
    with tempfile.NamedTemporaryFile(suffix=".nii.gz") as temp_nifti:
        dcm_nifti.save(temp_nifti.name)
        dcm_nifti = nib.load(temp_nifti.name)

        # convert both niftis to images
        nifti_imgs, _ = convert_nifti_to_images(nifti)
        dcm_nifti_imgs, _ = convert_nifti_to_images(dcm_nifti)

        nifti_img = nifti_imgs[0]
        dcm_nifti_img = dcm_nifti_imgs[0]

        # compare if the np arrays are equal
        assert np.array_equal(nifti_img, dcm_nifti_img)
