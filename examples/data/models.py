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
Radstract supports converting NIFTI Labels into 3D Models.
"""

from radstract.data.models import create_model_from_nifti
from radstract.testdata import Cases, download_case

dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

# Convert NIFTI to 3D Models
model = create_model_from_nifti(seg_file)

# save the model
model.export("debug/nifti-2-model.ply")
