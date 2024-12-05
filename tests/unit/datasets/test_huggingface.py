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

import os
import tempfile

from datasets import Dataset, DatasetDict, Image
from radstract.datasets.huggingface import make_huggingface_datadict


def test_make_huggingface_datadict():
    # Create a temporary directory for the test dataset
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the dataset directory structure
        os.makedirs(os.path.join(temp_dir, "images", "train"))
        os.makedirs(os.path.join(temp_dir, "images", "val"))
        os.makedirs(os.path.join(temp_dir, "labels", "train"))
        os.makedirs(os.path.join(temp_dir, "labels", "val"))

        # Create dummy image and label files
        for i in range(10):
            with open(
                os.path.join(temp_dir, "images", "train", f"image_{i}.jpg"),
                "w",
            ) as f:
                f.write("dummy image")
            with open(
                os.path.join(temp_dir, "labels", "train", f"label_{i}.png"),
                "w",
            ) as f:
                f.write("dummy label")
            with open(
                os.path.join(temp_dir, "images", "val", f"image_{i}.jpg"), "w"
            ) as f:
                f.write("dummy image")
            with open(
                os.path.join(temp_dir, "labels", "val", f"label_{i}.png"), "w"
            ) as f:
                f.write("dummy label")

        # Call the function with the test dataset directory
        dataset_test = make_huggingface_datadict(
            temp_dir, dataset_fraction=0.5
        )

        # Assert the returned object is a DatasetDict
        assert isinstance(dataset_test, DatasetDict)

        # Assert the DatasetDict contains the expected splits
        assert "train" in dataset_test
        assert "validation" in dataset_test

        # Assert the datasets have the expected number of samples
        assert len(dataset_test["train"]) == 5
        assert len(dataset_test["validation"]) == 5

        # Assert the datasets have the expected columns
        assert "image" in dataset_test["train"].column_names
        assert "label" in dataset_test["train"].column_names
        assert "image" in dataset_test["validation"].column_names
        assert "label" in dataset_test["validation"].column_names

        # Assert the columns have the expected types
        assert isinstance(dataset_test["train"].features["image"], Image)
        assert isinstance(dataset_test["train"].features["label"], Image)
        assert isinstance(dataset_test["validation"].features["image"], Image)
        assert isinstance(dataset_test["validation"].features["label"], Image)
