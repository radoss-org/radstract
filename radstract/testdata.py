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
Provides a convenient way to download test data for the Retuve library.
"""

import os
import uuid
from enum import Enum

import requests

URL = "https://github.com/radoss-org/radoss-creative-commons/raw/185aed296005617d13bc959b9e2853749c524586"


class Cases(Enum):
    """
    The test cases available for download.
    """

    ULTRASOUND_DICOM = [
        f"{URL}/dicoms/ultrasound/171551.dcm",
        f"{URL}/labels/ultrasound/171551.nii.gz",
    ]

    ULTRASOUND_NIFTI = [
        f"{URL}/other/ultrasound/172535-images.nii.gz",
        f"{URL}/labels/ultrasound/172535.nii.gz",
    ]

    ULTRASOUND_DICOM_DATASET = [
        f"{URL}/dicoms/ultrasound/171551.dcm",
        f"{URL}/dicoms/ultrasound/172534.dcm",
        f"{URL}/dicoms/ultrasound/172536.dcm",
        f"{URL}/labels/ultrasound/171551.nii.gz",
        f"{URL}/labels/ultrasound/172534.nii.gz",
        f"{URL}/labels/ultrasound/172536.nii.gz",
    ]

    XRAY_DCM = [
        f"{URL}/dicoms/xray/331_DDH_10.dcm",
    ]

    ULTRAOUND_NIFTI_TEST = [
        f"{URL}/labels/ultrasound/172658.nii.gz",
        f"{URL}/other/ultrasound/172658_14_labels.png",
    ]

    ULTRASOUND_DICOM_NIFTI_TEST = [
        f"{URL}/dicoms/ultrasound/172535.dcm",
        f"{URL}/other/ultrasound/172535-images.nii.gz",
    ]

    ULTRASOUND_REPORT_TEST = [
        f"{URL}/other/ultrasound/172535.mp4",
        f"{URL}/other/ultrasound/172535_0.png",
        "https://avatars.githubusercontent.com/u/167651866?s=400&u=c8a5acfe71d886fc8d3ed2f11fa6997fd673fefd&v=4.jpg",
    ]


def download_case(case: Cases, directory: str = None, temp=True, silent=True) -> list:
    """
    Download the test data for the given case

    :param case: The Case
    :param directory: The directory to download the files to
    :param temp: Whether to download the files to a temporary directory
    :param silent: Whether to print the download status

    :return: The filenames of the downloaded files

    Note that when directory is provided, temp is ignored.
    """
    if directory:
        temp = False

    if temp:
        # the directory should be in /tmp with a short uuid
        directory = f"/tmp/radstract-testdata/{uuid.uuid4()}"

    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    filenames = []

    for index, url in enumerate(case.value):

        url_filename = url.split("/")[-1]
        # Extract the filename from the URL
        filename = os.path.join(directory, url_filename)

        # check if the file already exists
        if os.path.exists(filename):
            filenames.append(filename)
            continue

        # Download the file
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as file:
                file.write(response.content)
            if not silent:
                print(f"Downloaded {filename}")
        else:
            print(f"Failed to download {url}, status code: {response.status_code}")

        filenames.append(filename)

    return filenames
