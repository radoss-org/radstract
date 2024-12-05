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
Calculates the angle between 3 points in a point cloud based
on the files generated by the 3D and 2D models, over a set of random points.

Based on https://graphics.stanford.edu/courses/cs468-08-fall/pdf/osada.pdf

Adding another model requires changes to
the constants in pavlic/models/common.py and
importing the new model.

Example: https://github.com/radoss-org/Radstract/tree/main/examples/analysis/shapedistro.py
"""

import numpy as np
import trimesh


def calculate_a3(
    trimesh_object: trimesh.Trimesh, num_of_samples: int = 1000
) -> np.ndarray:
    """
    Calculates the angle between 3 points in a point cloud based
    on the files generated by the 3D and 2D models, over a set
    of random points.

    :param trimesh_object: A trimesh object
    :param num_of_samples: The number of samples to take

    :return: An array of angles
    """

    # Get Points
    points = trimesh_object.vertices

    # Sample indices for random triples
    n = len(points)
    indices = np.random.default_rng(42).choice(n, size=(num_of_samples, 3))

    # Calculate angles
    v1 = points[indices[:, 0]]
    v2 = points[indices[:, 1]]
    v3 = points[indices[:, 2]]
    vectors1 = v1 - v2
    vectors2 = v3 - v2

    dot_products = np.sum(vectors1 * vectors2, axis=-1)

    # Normalize vectors
    norms1 = np.linalg.norm(vectors1, axis=-1)
    norms2 = np.linalg.norm(vectors2, axis=-1)

    # Deals with any invalid values
    with np.errstate(invalid="ignore"):
        angles = np.arccos(dot_products / (norms1 * norms2))

    # remove nans from invalid angles
    angles = np.rad2deg(angles)
    angles = angles[~np.isnan(angles)]

    return angles
