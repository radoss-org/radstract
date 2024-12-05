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

import numpy as np
import pydicom
from PIL import Image

from radstract.data.dicom import convert_dicom_to_images


def test_convert_dicom_to_images(ultrasound_dcm, ultrasound_label_slice0):
    old_dicom = pydicom.dcmread(ultrasound_dcm)

    images = convert_dicom_to_images(old_dicom)

    assert isinstance(images, list)
    assert len(images) > 0
    assert all(isinstance(img, Image.Image) for img in images)

    # Compare the first image with the test image
    test_image = Image.open(ultrasound_label_slice0).convert("RGB")

    # NOTE(2024-04-20 Sharpz7) Slight difference in pixel values due to conversion
    assert np.allclose(np.array(images[0]), np.array(test_image), atol=3)
