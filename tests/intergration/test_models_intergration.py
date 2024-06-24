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
