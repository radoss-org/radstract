import logging
from typing import Dict, List, Tuple

import cv2
import numpy as np
from PIL import Image

from radstract.data.colors import LabelColours, get_unique_colours


def segmentation_to_polygons(
    seg_image: Image.Image,
) -> Dict[int, List[List[int]]]:
    """
    Convert segmentation mask to a list of polygons.

    :param seg_image: PIL Image: Segmentation mask image.

    :return: dict: Dictionary of polygons for each class.
    """
    # Load segmentation mask
    mask = np.array(seg_image)

    polygons = {}

    for mask_colour in get_unique_colours(array=mask):
        if mask_colour == (0, 0, 0):
            continue

        color_mask = np.all(mask == mask_colour, axis=-1)

        segment_mask = np.zeros_like(mask)
        segment_mask[color_mask] = 255

        # convert to grayscale
        segment_mask = cv2.cvtColor(segment_mask, cv2.COLOR_BGR2GRAY)

        # Find contours of the segment
        contours, _ = cv2.findContours(
            segment_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        # Approximate contours to polygons and add them to the list
        for contour in contours:
            epsilon = 0.01 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            polygon = approx.squeeze().tolist()

            key = LabelColours.get_colour_key(mask_colour)
            polygons.setdefault(key, []).append(polygon)

    return polygons


def get_polygon_annotations(
    polygons: Dict[int, List[List[int]]], image_shape: Tuple[int, int]
) -> List[str]:
    """
    Save the polygon annotations

    :param polygons: dict: Dictionary of polygons for each class.
    :param image_shape: tuple: Image dimensions (width, height).

    :return: list: List of annotations
    """

    width, height = image_shape
    lines = []

    try:
        for colour_key in polygons.keys():
            for polygon in polygons[colour_key]:
                # Normalize the polygon coordinates (0 to 1 scale) based on the image dimensions
                normalized_polygon = [
                    (x / width, y / height) for x, y in polygon
                ]

                line = f"{colour_key} " + " ".join(
                    f"{x:.6f} {y:.6f}" for x, y in normalized_polygon
                )

                lines.append(line)

    except Exception as e:
        logging.error(f"Error in get_polygon_annotations: {e}")
        return None

    return lines
