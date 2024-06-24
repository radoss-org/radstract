import os

import pytest

from radstract.datasets.nnunet import generate_nnunet_dataset_json


@pytest.fixture
def nnunet_dir_structure():
    return {
        "imagesTr": "path/to/imagesTr",
        "imagesTs": "path/to/imagesTs",
        "labelsTr": "path/to/labelsTr",
    }


def test_generate_nnunet_dataset_json(nnunet_dir_structure, monkeypatch):
    # Mock the os.listdir function to return a list of files
    def mock_listdir(path):
        if path == nnunet_dir_structure["imagesTr"]:
            return ["image1.nii.gz", "image2.nii.gz"]
        elif path == nnunet_dir_structure["imagesTs"]:
            return ["image3.nii.gz"]
        else:
            return []

    monkeypatch.setattr(os, "listdir", mock_listdir)

    dataset_name = "Test Dataset"
    modalities = {
        0: "CT",
    }
    labels = {0: "Background", 1: "Tumor"}

    result = generate_nnunet_dataset_json(
        nnunet_dir_structure, dataset_name, modalities, labels
    )

    assert result["name"] == dataset_name
    assert result["description"] == "Dataset for nnU-Net model"
    assert result["tensorImageSize"] == "4D"
    assert result["modality"] == modalities
    assert result["labels"] == labels
    assert result["numTraining"] == 2
    assert result["numTest"] == 1
    assert result["training"] == [
        {
            "image": "./imagesTr/image1.nii.gz",
            "label": "./labelsTr/image1.nii.gz",
        },
        {
            "image": "./imagesTr/image2.nii.gz",
            "label": "./labelsTr/image2.nii.gz",
        },
    ]
    assert result["test"] == [
        {
            "image": "./imagesTs/image3.nii.gz",
            "label": "./labelsTr/image3.nii.gz",
        },
    ]


def test_generate_nnunet_dataset_json_empty_directories(
    nnunet_dir_structure, monkeypatch
):
    # Mock the os.listdir function to return empty lists
    monkeypatch.setattr(os, "listdir", lambda _: [])

    dataset_name = "Empty Dataset"
    modalities = ["CT"]
    labels = {0: "Background"}

    result = generate_nnunet_dataset_json(
        nnunet_dir_structure, dataset_name, modalities, labels
    )

    assert result["numTraining"] == 0
    assert result["numTest"] == 0
    assert result["training"] == []
    assert result["test"] == []
