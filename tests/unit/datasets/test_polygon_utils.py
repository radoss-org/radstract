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
from PIL import Image

from radstract.datasets.polygon_utils import (
    get_polygon_annotations,
    segmentation_to_polygons,
)


def test_get_polygon_annotations():
    # Define test polygons
    polygons = {
        0: [[[10, 20], [30, 40], [50, 60]]],
        1: [
            [[70, 80], [90, 100], [110, 120]],
            [[130, 140], [150, 160], [170, 180]],
        ],
    }

    # Define test image shape
    image_shape = (200, 300)

    # Call the function
    annotations = get_polygon_annotations(polygons, image_shape)

    # Define the expected annotations
    expected_annotations = [
        "0 0.050000 0.066667 0.150000 0.133333 0.250000 0.200000",
        "1 0.350000 0.266667 0.450000 0.333333 0.550000 0.400000",
        "1 0.650000 0.466667 0.750000 0.533333 0.850000 0.600000",
    ]

    # Assert that the returned annotations match the expected annotations
    assert annotations == expected_annotations


def test_get_polygon_annotations_empty_polygons():
    # Define empty polygons
    polygons = {}

    # Define test image shape
    image_shape = (200, 300)

    # Call the function
    annotations = get_polygon_annotations(polygons, image_shape)

    # Assert that an empty list is returned
    assert annotations == []


def test_get_polygon_annotations_exception():
    # Define invalid polygons (missing coordinates)
    polygons = {
        0: [[[10, 20], [30]]],
    }

    # Define test image shape
    image_shape = (200, 300)

    # Call the function
    annotations = get_polygon_annotations(polygons, image_shape)

    # Assert that None is returned when an exception occurs
    assert annotations is None


def create_test_segmentation_image():
    # Create a test segmentation image
    image_data = [
        [(255, 0, 0), (255, 0, 0), (0, 255, 0)],
        [(255, 0, 0), (0, 0, 0), (0, 255, 0)],
        [(0, 0, 255), (0, 0, 255), (0, 255, 0)],
    ]
    return Image.fromarray(np.array(image_data, dtype=np.uint8))


def test_segmentation_to_polygons():
    # Create a test segmentation image
    seg_image = create_test_segmentation_image()

    # Call the function
    polygons = segmentation_to_polygons(seg_image)

    # Define the expected polygons
    expected_polygons = {
        2: [[[2, 0], [2, 2]]],
        1: [[[1, 0], [0, 0], [0, 1]]],
        3: [[[0, 2], [1, 2]]],
    }

    # Assert that the returned polygons match the expected polygons
    assert polygons == expected_polygons
