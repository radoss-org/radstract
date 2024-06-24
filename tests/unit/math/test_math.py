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
