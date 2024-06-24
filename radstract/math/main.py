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
