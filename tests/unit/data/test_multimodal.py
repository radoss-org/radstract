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

from PIL import Image

from radstract.data.multimodal import remove_black_frames

ALL_BLACK = Image.new("RGB", (100, 100), (0, 0, 0))

LABELLED_IMAGE = Image.new("RGB", (100, 100), (255, 255, 255))
NON_LABELLED_IMAGE = Image.new("RGB", (100, 100), (0, 0, 0))


def test_remove_black_frames():
    dicom_list = [ALL_BLACK, NON_LABELLED_IMAGE]
    nifti_list = [ALL_BLACK, LABELLED_IMAGE]

    dicom_list, nifti_list = remove_black_frames(dicom_list, nifti_list)

    assert len(dicom_list) == 1
    assert len(nifti_list) == 1
    assert dicom_list[0] == NON_LABELLED_IMAGE
    assert nifti_list[0] == LABELLED_IMAGE
