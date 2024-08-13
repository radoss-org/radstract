import os
from typing import List, Optional, Tuple, Union

from h11 import Data
from PIL import Image

from radstract.data.dicom import DicomTypes

from .polygon_utils import get_polygon_annotations, segmentation_to_polygons
from .utils import DataSplit, convert_dcm_nii_dataset


def convert_dataset_to_polygons(
    input_dir: str,
    output_dir: str,
    processes: int = 1,
    crop_coordinates: Tuple[int, int, int, int] = None,
    dicom_type: DicomTypes = DicomTypes.DEFAULT,
    data_split: Union[Tuple[float, float], DataSplit] = DataSplit(),
    color_changes: List[Tuple[int, int, int]] = None,
    min_polygons: int = 6,
) -> None:
    """
    Convert a dataset in the input_dir to a .txt polygon format
    and save it to the output_dir.

    :param input_dir: str: Path to the input directory.
    :param output_dir: str: Path to the output directory.
    :param processes: int: Number of processes to use.
    :param crop_coordinates: tuple: Crop coordinates for the images.
    :param dicom_type: DicomTypes: Type of DICOM file.
    :param data_split: tuple, DataSplit: Data split percentages.
    :param color_changes: list: List of colour changes.
    :param min_polygons: int: Minimum number of polygons to consider.

    :return: None
    """

    # create the output directory, train, val and test directories
    os.makedirs(output_dir, exist_ok=True)
    for split in ["images", "labels"]:
        os.makedirs(os.path.join(output_dir, split), exist_ok=True)
        for split_dir in ["train", "val", "test"]:
            os.makedirs(
                os.path.join(output_dir, split, split_dir), exist_ok=True
            )

    # Convert the dataset to a Huggingface DatasetDict
    convert_dcm_nii_dataset(
        input_dir,
        output_dir,
        processes=processes,
        crop_coordinates=crop_coordinates,
        dicom_type=dicom_type,
        data_split=data_split,
        color_changes=color_changes,
        file_pair_kwargs={"min_polygons": min_polygons},
        save_func=save_polygons,
    )


def save_polygons(
    dicom_image: Image.Image,
    seg_image: Image.Image,
    image_dir: str,
    label_dir: str,
    file_name: str,
    file_pair_kwargs: Optional[dict] = None,
):
    """
    Save the image and polygon annotations.

    :param dicom_image: PIL.Image: DICOM image.
    :param seg_image: PIL.Image: Segmentation mask image.
    :param image_dir: str: Directory to save the image.
    :param label_dir: str: Directory to save the annotations.
    :param file_name: str: File name for the image and annotations.
    :param file_pair_kwargs: dict: Keyword arguments for the file pair.

    :return: None
    """
    dicom_image.save(os.path.join(image_dir, f"{file_name}.jpg"), "JPEG")

    min_polygons = file_pair_kwargs.get("min_polygons", 6)

    temp_dict = segmentation_to_polygons(seg_image)
    polygons = {}

    for key in temp_dict.keys():
        polygons[key - 1] = temp_dict[key]

    # remove any polygons with less than 6 points
    for key, value in polygons.items():
        polygons[key] = [
            polygon for polygon in value if len(polygon) >= min_polygons
        ]

    lines = get_polygon_annotations(polygons, image_shape=dicom_image.size)
    if lines:
        # Save annotations
        with open(os.path.join(label_dir, f"{file_name}.txt"), "w") as f:
            f.write("\n".join(lines))
