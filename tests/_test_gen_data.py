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

import json
import os
import shutil

import cv2
import numpy as np
import pydicom
import pytest
import trimesh
from matplotlib.pylab import f
from PIL import Image

from radstract.analysis.shapedistro.models import (
    COMPARISON_BINS,
    ShapeDistroModels,
    calculate_a3,
    calculate_d2,
    generate_distribution,
)
from radstract.data import dicom
from radstract.data.dicom import (
    DicomTypes,
    convert_dicom_to_images,
    convert_images_to_dicom,
)
from radstract.data.images import NoiseReductionFilter, reduce_noise
from radstract.data.models import create_model_from_nifti
from radstract.datasets.huggingface import convert_dataset_to_huggingface
from radstract.datasets.nnunet import (
    build_nnunet_dir_structure,
    convert_dataset_to_nnunet,
    generate_nnunet_dataset_json,
)
from radstract.datasets.polygon import convert_dataset_to_polygons
from radstract.datasets.utils import DataSplit
from radstract.testdata import Cases, download_case

# create test_data dir
if os.path.exists("./tests/test_data/"):
    # remove existing test_data
    shutil.rmtree("./tests/test_data/")
os.makedirs("./tests/test_data/")

dcm_file, *_ = download_case(
    Cases.ULTRASOUND_DICOM_DATASET, directory="./tests/test_data/dataset"
)


def create_datasets():
    DATASET_DIR = os.path.join(os.path.dirname(dcm_file))
    OUTPUT_DIR = "./tests/test_data/post_created_datasets"

    # create output dir
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    polygon_dir = os.path.join(OUTPUT_DIR, "polygon")
    huggingface_dir = os.path.join(OUTPUT_DIR, "huggingface")
    nnunet_dir = os.path.join(OUTPUT_DIR, "nnunet")

    convert_dataset_to_polygons(
        input_dir=DATASET_DIR,
        output_dir=polygon_dir,
        processes=8,
        crop_coordinates=None,
        dicom_type=DicomTypes.SERIES,
        data_split=DataSplit(0.5, 0.5, 0),
        color_changes=None,
        min_polygons=6,
    )

    convert_dataset_to_huggingface(
        input_dir=DATASET_DIR,
        output_dir=huggingface_dir,
        processes=8,
        crop_coordinates=None,
        dicom_type=DicomTypes.SERIES,
        data_split=DataSplit(0.5, 0.5, 0),
        color_changes=None,
    )

    convert_dataset_to_nnunet(
        input_dir=DATASET_DIR,
        output_dir=nnunet_dir,
        processes=8,
        crop_coordinates=None,
        dicom_type=DicomTypes.SERIES,
        data_split=DataSplit(0.5, 0.5, 0),
        color_changes=None,
    )

    nnunet_dir_structure = build_nnunet_dir_structure(nnunet_dir)

    dataset_json = generate_nnunet_dataset_json(
        nnunet_dir_structure,
        dataset_name="HipUltrasound",
        modalities={0: "US"},
        labels={
            0: "Background",
        },
        description="Dataset for Hip Ultrasound",
        reference="Put your reference here",
        licence="Dataset license",
        release="1.0",
    )

    with open(f"{nnunet_dir}/dataset.json", "w") as f:
        json.dump(dataset_json, f, indent=4)


def create_dicom_data():
    dcm_us, seg_file = download_case(Cases.ULTRASOUND_DICOM)

    dcm = pydicom.dcmread(dcm_us)

    images = convert_dicom_to_images(dcm)

    file_name = dcm_us.split("/")[-1].split(".")[0]

    images[0].save(f"./tests/test_data/{file_name}_slice0.png")

    def custom_filter(image):
        # Apply custom filtering operations to the image
        # For example, let's apply a simple threshold
        _, filtered_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
        return filtered_image

    noise_img = reduce_noise(
        images[0],
        [
            NoiseReductionFilter.MEDIAN_FILTER(size=5),
            NoiseReductionFilter.GAUSSIAN_BLUR(kernel_size=(5, 5)),
            NoiseReductionFilter.BILATERAL_FILTER(
                diameter=9, sigma_color=75, sigma_space=75
            ),
            NoiseReductionFilter.LAMBDA_FILTER(func=custom_filter),
        ],
    )

    noise_img.save(f"./tests/test_data/{file_name}_slice0_noise.png")


def create_shape_distro_data():
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
    faces = np.array([[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])
    sample_trimesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    for model in ShapeDistroModels.ALL:
        bin_centers, hist = generate_distribution(sample_trimesh, model)

        np.savez(
            f"tests/test_data/{model}.npz", bin_centers=bin_centers, hist=hist
        )


def create_dicoms_for_testing_validity_in_major_programs():
    dcm_us, seg_file = download_case(Cases.ULTRASOUND_DICOM)
    dcm = pydicom.dcmread(dcm_us)
    images = convert_dicom_to_images(dcm)

    # once uncompressed
    new_dcm = convert_images_to_dicom(images)

    new_dcm_compressed = convert_images_to_dicom(images, compress_ratio=15)

    new_dcm.save_as("./tests/test_data/ultrasound.dcm")
    new_dcm_compressed.save_as("./tests/test_data/ultrasound_compressed.dcm")

    # also test a single-image DICOM
    single_image = images[0]

    new_single_dcm = convert_images_to_dicom(
        [single_image],
        dicom_type=DicomTypes.SINGLE_ANONYMIZED,
        compress_ratio=5,
    )

    new_single_dcm.save_as("./tests/test_data/ultrasound_single.dcm")


def create_3d_model_data():
    dcm_us, seg_file = download_case(Cases.ULTRASOUND_DICOM)

    model = create_model_from_nifti(seg_file)

    filename = seg_file.split("/")[-1].split(".")[0]

    # save trimesh
    model.export(f"./tests/test_data/{filename}.ply")


if __name__ == "__main__":
    create_datasets()
    create_dicom_data()
    create_shape_distro_data()
    create_3d_model_data()
    create_dicoms_for_testing_validity_in_major_programs()

    # Create a print statement warning people
    # to make sure the DICOMs open in major programs (Like ITK-SNAP)
    print(
        "\nWARNING\n"
        "==================\n"
        "Please make sure the DICOM files in tests/test_data/ultrasound.dcm "
        ", tests/test_data/ultrasound_compressed.dcm and tests/test_data/ultrasound_single.dcm "
        "open in major programs (Like ITK-SNAP) before committing."
    )
