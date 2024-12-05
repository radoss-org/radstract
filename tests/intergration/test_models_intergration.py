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
import trimesh

from radstract.data.models import create_model_from_nifti


def test_create_model_from_nifti(ultrasound_nifti_labels, model_3d):
    test = create_model_from_nifti(ultrasound_nifti_labels)

    # NOTE((2024-04-20 Sharpz7)): This tolerance is needed because
    # trimesh does some rounding on the vertices
    test_ply = trimesh.load(model_3d)
    assert np.allclose(test.vertices, test_ply.vertices, rtol=0.0001)
    assert np.allclose(test.faces, test_ply.faces, rtol=0.0001)
