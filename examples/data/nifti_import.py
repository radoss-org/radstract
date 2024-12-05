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
Radstract supports converting NIFTI files of
two different types to labelled images:

- Labelled NIFTI's
- Image NIFTI's
"""

from radstract.data.nifti import (
    convert_nifti_to_image_labels,
    convert_nifti_to_images,
)
from radstract.testdata import Cases, download_case

nii_images, nii_labels = download_case(Cases.ULTRASOUND_NIFTI)

# Quickly get some example labels
images, _ = convert_nifti_to_image_labels(nii_labels)
images[0].save("debug/nifti_creation_labels.png")

# Quickly get some example images
images, _ = convert_nifti_to_images(nii_images)
images[0].save("debug/nifti_creation_images.png")
