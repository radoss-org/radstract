import numpy as np
from PIL import Image

from radstract.data.colors import (
    LabelColours,
    change_color,
    convert_labels_to_image,
    fast_check_all_black,
    get_unique_colours,
)

ALL_BLACK = Image.new("RGB", (100, 100), (0, 0, 0))
ALL_WHITE = Image.new("RGB", (100, 100), (255, 255, 255))


MULTI_COLOR_IMAGE = Image.new("RGB", (100, 100), (0, 0, 0))
MULTI_COLOR_IMAGE.paste((255, 0, 0), (0, 0, 50, 50))
MULTI_COLOR_IMAGE.paste((0, 255, 0), (50, 0, 100, 50))
MULTI_COLOR_IMAGE.paste((0, 0, 255), (0, 50, 50, 100))
COLORS = ((0, 255, 0), (255, 0, 0), (0, 0, 0), (0, 0, 255))

SEGMENTATION_ARRAY = np.full((100, 100), 1, dtype=np.uint8)
ALL_RED_ARRAY = np.full((100, 100, 3), (255, 0, 0), dtype=np.uint8)


def test_label_colours():
    assert LabelColours.get_colour_key((0, 0, 0)) == 0
    assert LabelColours.get_colour_key((255, 0, 0)) == 1
    assert LabelColours.get_colour_key((0, 255, 0)) == 2
    assert LabelColours.get_colour_key((0, 0, 255)) == 3
    assert LabelColours.get_colour_key((255, 255, 0)) == 4
    assert LabelColours.get_colour_key((0, 128, 128)) == 5
    assert LabelColours.get_colour_key((128, 0, 128)) == 6
    assert LabelColours.get_color_from_index(5) == (0, 128, 128)
    assert LabelColours.get_color_from_index(6) == (128, 0, 128)
    assert LabelColours.get_color_from_index(7) == (111, 110, 218)
    assert LabelColours.get_colour_key((111, 110, 218)) == 7


def test_get_unique_colours():
    assert (
        get_unique_colours(img=MULTI_COLOR_IMAGE) == COLORS
    ), get_unique_colours(img=MULTI_COLOR_IMAGE)
    assert (
        get_unique_colours(array=np.array(MULTI_COLOR_IMAGE)) == COLORS
    ), get_unique_colours(array=np.array(MULTI_COLOR_IMAGE))


def test_change_color():
    assert change_color(ALL_BLACK, (0, 0, 0), (255, 255, 255)) == ALL_WHITE


def test_convert_labels_to_image():
    assert np.array_equal(
        convert_labels_to_image(SEGMENTATION_ARRAY), ALL_RED_ARRAY
    )


def test_all_black():
    assert fast_check_all_black(ALL_BLACK)
    assert not fast_check_all_black(ALL_WHITE)
