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
Smart Intersection Finder (Can handle vertical and horizontal lines)

Examples: https://github.com/radoss-org/Radstract/tree/main/examples/math/smart_intersection.py
"""

from typing import Tuple

# create coordinate type
Coordinate = Tuple[int, int]


def smart_find_intersection(
    point1a: Coordinate,
    point1b: Coordinate,
    point2a: Coordinate,
    point2b: Coordinate,
) -> Coordinate:
    """
    Returns the intersection point of the two lines.

    Can handle vertical and horizontal lines.

    Line1: point1a, point1b
    Line2: point2a, point2b
    """
    x1, y1 = point1a
    x2, y2 = point1b
    x3, y3 = point2a
    x4, y4 = point2b

    # Calculate the differences
    dx1 = x2 - x1
    dy1 = y2 - y1
    dx2 = x4 - x3
    dy2 = y4 - y3

    # Calculate the determinant
    determinant = dx1 * dy2 - dy1 * dx2

    if determinant == 0:
        raise ValueError("Lines are parallel")

    # Calculate the intersection point
    x = -((x1 * y2 - y1 * x2) * dx2 - (x3 * y4 - y3 * x4) * dx1) / determinant
    y = -((x1 * y2 - y1 * x2) * dy2 - (x3 * y4 - y3 * x4) * dy1) / determinant

    return int(x), int(y)
