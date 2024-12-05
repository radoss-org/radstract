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
Generate a distribution of the given model for the given trimesh object.

Example: https://github.com/radoss-org/Radstract/tree/main/examples/analysis/shapedistro.py
"""

from typing import Tuple

import numpy as np
import trimesh

from .a3 import calculate_a3
from .d2 import calculate_d2


class ShapeDistroModels:
    A3 = "a3"
    D2 = "d2"

    ALL = [
        A3,
        D2,
    ]


# Number of Histogram Bins for the individual histograms
COMPARISON_BINS = 20


def generate_distribution(
    trimesh_object: trimesh.Trimesh, model: ShapeDistroModels
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a distribution of the given model for the given trimesh object.

    :param trimesh_object: The trimesh object to generate the distribution for.
    :param model: The model to use for generating the distribution.

    :return: A tuple containing the bin centers and the histogram values.

    :raises ValueError: If an invalid model is provided.
    """

    if model not in ShapeDistroModels.ALL:
        raise ValueError(f"Invalid model: {model}")

    if model == ShapeDistroModels.A3:
        data = calculate_a3(trimesh_object)
    elif model == ShapeDistroModels.D2:
        data = calculate_d2(trimesh_object)

    # Normalize the data by their mean
    data = data / np.mean(data)

    # Calculate histograms for both files
    hist, bins = np.histogram(data, bins=COMPARISON_BINS, density=True)

    # Calculate bin centers
    bin_centers = (bins[:-1] + bins[1:]) / 2

    return bin_centers, hist
