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

"""
Radstract has a direct function for converting
DICOM's to NIfTI files.

As well as this, when working with DICOMs and NIFTI Labels,
you can remove frames with no labels with a simple function.
"""

import pydicom

from radstract.data.dicom import convert_dicom_to_images
from radstract.testdata import Cases, download_case

dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

# Convert DICOM to NIFTI
dcm = pydicom.dcmread(dcm_file)

dicom_images = convert_dicom_to_images(dcm)

# save the first image
dicom_images[0].save("debug/dicom-2-image.png")
