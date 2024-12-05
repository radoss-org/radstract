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
Radstract supportd creating DICOM files from images.

This is an experimental feature, and is not recommended for production use.
"""

from PIL import Image

from radstract.data.dicom import convert_images_to_dicom

# create random noise image
image = Image.new("RGB", (512, 512))

images = [image, image]

# convert images to dicom
dcm = convert_images_to_dicom(images)

# save dicom
dcm.save_as("debug/dicom_creation.dcm")
