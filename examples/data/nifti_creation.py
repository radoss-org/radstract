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
Radstract supports converting labelled images to NIFTI files.
"""

from radstract.data.nifti import (
    convert_images_to_nifti_labels,
    convert_nifti_to_image_labels,
)
from radstract.testdata import Cases, download_case

dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

# Quickly get some example labels
images, _ = convert_nifti_to_image_labels(seg_file)

# convert those images to NIFTI
nii = convert_images_to_nifti_labels(images)

# save the NIFTI
nii.save("debug/nifti_creation.nii.gz")
