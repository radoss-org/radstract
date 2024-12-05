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
The main algorithm for converting NII files to PLY files.

Examples:
https://github.com/radoss-org/Radstract/tree/main/examples/data/models.py
"""

from typing import List, Tuple, Union

import nibabel as nib
import numpy as np
import trimesh
from nibabel import Nifti1Image
from skimage import measure
from trimesh.smoothing import filter_humphrey

from radstract.data.colors import LabelColours

DEFAULT_LABELS = np.array(
    [
        [0, 0, 0],
        LabelColours.LABEL1,
        LabelColours.LABEL2,
        LabelColours.LABEL3,
        LabelColours.LABEL4,
        LabelColours.LABEL5,
        LabelColours.LABEL6,
    ]
)


def create_model_from_nifti(
    nii_file: Union[str, Nifti1Image]
) -> trimesh.Trimesh:
    """
    Create a model from a nii file.

    :param nii_file: The nii file or the path to the nii file

    :return: The model file
    """

    if isinstance(nii_file, str):
        # Updates and loads the nii file
        nii_file = nib.load(nii_file)

    np_array = nii_file.get_fdata()  # type: ignore [attr-defined]

    # Apply pixdim to get the right scale
    verts, faces, _, values = measure.marching_cubes(
        np_array, 0, step_size=5, spacing=[0.1, 0.1, 0.1]
    )
    values = values.astype(int)

    # Calculate the center of mass of the vertices
    # Subtract the center of mass from each vertex
    center_of_mass = verts.mean(axis=0)
    verts = verts - center_of_mass

    vertex_colors = get_vertex_colours(verts, values)

    mesh = trimesh.Trimesh(
        vertices=verts, faces=faces, vertex_colors=vertex_colors
    )

    # Smooth the mesh
    smoothed = filter_humphrey(mesh, iterations=10, alpha=0.2, beta=0.6)

    return smoothed


def get_vertex_colours(
    verts: np.ndarray,
    values: np.ndarray,
    colors: List[Tuple[int, int, int]] = DEFAULT_LABELS,
) -> np.ndarray:
    """
    Get the vertex colours for the model.

    :param verts: The vertices of the model
    :param values: The values of the model
    :param colors: The colours for the labels of the segmentation

    :return: The vertex colours
    """

    # apply the colors to the vertices according to their segmentation label
    vertex_colors = colors[values]

    # f4 = float32, u1 = uint8
    vertex_data = np.zeros(
        verts.shape[0],
        dtype=[
            ("x", "f4"),
            ("y", "f4"),
            ("z", "f4"),
            ("red", "u1"),
            ("green", "u1"),
            ("blue", "u1"),
        ],
    )
    vertex_data["x"], vertex_data["y"], vertex_data["z"] = verts.T
    (
        vertex_data["red"],
        vertex_data["green"],
        vertex_data["blue"],
    ) = vertex_colors.T

    return vertex_data
