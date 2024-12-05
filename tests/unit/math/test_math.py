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

import pytest

from radstract.math import smart_find_intersection


def test_smart_find_intersection():
    # Test case 1: Intersection of two non-vertical, non-horizontal lines
    point1 = (0, 0)
    point2 = (4, 4)
    point3 = (0, 4)
    point4 = (4, 0)
    assert smart_find_intersection(point1, point2, point3, point4) == (2, 2)

    # Test case 2: Intersection of a vertical line and a non-vertical line
    point1 = (2, 0)
    point2 = (2, 4)
    point3 = (0, 2)
    point4 = (4, 2)
    assert smart_find_intersection(point1, point2, point3, point4) == (2, 2)

    # Test case 3: Intersection of a horizontal line and a non-horizontal line
    point1 = (0, 2)
    point2 = (4, 2)
    point3 = (2, 0)
    point4 = (2, 4)
    assert smart_find_intersection(point1, point2, point3, point4) == (2, 2)

    # Test case 4: Intersection of two vertical lines (raises ValueError)
    point1 = (2, 0)
    point2 = (2, 4)
    point3 = (2, 2)
    point4 = (2, 6)
    with pytest.raises(ValueError, match="Lines are parallel"):
        smart_find_intersection(point1, point2, point3, point4)
