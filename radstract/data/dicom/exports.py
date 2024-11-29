"""
This file contains all the code for exporting DICOMs.

Note that creating "empty" DICOMs from code is less common,
so this code is considered experimental.

Examples: https://github.com/radoss-org/Radstract/tree/main/examples/data/dicom_creation.py

"""

import random
import warnings
from io import BytesIO
from typing import List

import numpy as np
import pydicom
from PIL import Image
from pydicom.dataset import FileMetaDataset
from pydicom.uid import JPEG2000

from radstract.data.dicom.utils import DicomTypes

from .utils import DicomTypes


class PlaceHolderTag:
    UseOldTagStr = "UseOldTag"
    UseOldTagInt = 99999
    UseOldTagUID = "1.1"


def _get_bits_data(dicom: pydicom.Dataset) -> pydicom.Dataset:
    """
    Sets the default bits data for a new DICOM file.

    :param dicom: pydicom Dataset object.

    :return: pydicom Dataset object with bits data set.
    """
    dicom.SamplesPerPixel = 3
    dicom.PhotometricInterpretation = "RGB"
    dicom.PixelRepresentation = 0
    dicom.BitsStored = 8
    dicom.BitsAllocated = 8
    dicom.HighBit = 7

    return dicom


def _set_defaults(dicom: pydicom.Dataset) -> pydicom.Dataset:
    """
    Sets the default tags for a new DICOM file.

    :param dicom: pydicom Dataset object.

    :return: pydicom Dataset object with default tags set.
    """

    dicom.file_meta = FileMetaDataset()

    dicom.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.1"
    dicom.SOPClassUID = "1.2.840.10008.5.1.4.1.1.1"

    dicom.file_meta.MediaStorageSOPInstanceUID = PlaceHolderTag.UseOldTagUID
    dicom.file_meta.ImplementationClassUID = pydicom.uid.generate_uid()

    dicom.Manufacturer = "RADSTRACT"
    dicom.ImageType = ["DERIVED"]

    return dicom


def _set_series(dicom: pydicom.Dataset) -> pydicom.Dataset:
    """
    Sets the default series tags for a new DICOM file.

    :param dicom: pydicom Dataset object.

    :return: pydicom Dataset object with series tags set.
    """

    dicom.PixelSpacing = [1, 1]
    dicom.SliceThickness = 1

    # hasOrientation
    dicom.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]

    # hasPosition
    dicom.ImagePositionPatient = [0, 0, 0]

    return dicom


def add_anon_tags(
    dicom: pydicom.Dataset, keyint: int = None
) -> pydicom.Dataset:
    """
    Adds anonymization tags to a DICOM file.

    :param dicom: pydicom Dataset object.
    :param keyint: The key to use for anonymization.

    :return: pydicom Dataset object with anonymization tags set.
    """

    if keyint is None:
        keyint = random.randint(0, 1000000)

    key = f"radstract-{keyint}"

    dicom.SeriesInstanceUID = pydicom.uid.generate_uid()
    dicom.SOPInstanceUID = pydicom.uid.generate_uid()
    dicom.StudyInstanceUID = pydicom.uid.generate_uid()

    dicom.SeriesNumber = keyint

    dicom.PatientID = key
    dicom.StudyID = key

    return dicom


def create_empty_dicom(
    dicom_type=DicomTypes.DEFAULT, keyint: int = None
) -> pydicom.Dataset:
    """
    Creates a pyDICOM Dataset with default tags for a new DICOM file.

    :param dicom_type: The type of DICOM file to create.
    :param keyint: The key to use for anonymization.

    :return: pydicom Dataset object with default tags set.

    :raises NotImplementedError: If the DICOM type is not implemented.
    """

    if dicom_type not in DicomTypes.ALL_TYPES:
        raise NotImplementedError(
            f"Dicom type {dicom_type} not implemented yet. Please choose from {DicomTypes.ALL_TYPES}"
        )

    new_dicom = pydicom.Dataset()
    new_dicom = _get_bits_data(new_dicom)
    new_dicom = _set_defaults(new_dicom)

    if dicom_type in DicomTypes.ALL_SERIES:
        _set_series(new_dicom)

    if dicom_type in DicomTypes.ANON:
        new_dicom = add_anon_tags(new_dicom, keyint)

    else:
        new_dicom.SeriesNumber = PlaceHolderTag.UseOldTagInt

        # make the above more consize
        old_tags_str = [
            "PatientID",
            "PatientName",
            "StudyID",
        ]
        for tag in old_tags_str:
            setattr(new_dicom, tag, PlaceHolderTag.UseOldTagStr)

        old_tags_uid = [
            "SeriesInstanceUID",
            "SOPInstanceUID",
            "StudyInstanceUID",
        ]

        for tag in old_tags_uid:
            setattr(new_dicom, tag, PlaceHolderTag.UseOldTagUID)

    return new_dicom


def add_tags(
    empty_new_dicom: pydicom.Dataset, old_dicom: pydicom.Dataset
) -> pydicom.Dataset:
    """
    Replaces placeholder tags in the new DICOM dataset
    with values from the old DICOM dataset.
    This function now includes logic to handle sequences.

    :param empty_new_dicom: pydicom Dataset object.
    :param old_dicom: pydicom Dataset object.

    :return: New DICOM dataset with specified tags transferred.
    """

    def replace_tags(new_element, old_element):
        for tag in new_element.dir():
            # If it's a sequence, apply the logic recursively
            if isinstance(new_element[tag].value, pydicom.sequence.Sequence):
                # check old element has tag
                if not hasattr(old_element, tag):
                    warnings.warn(
                        f"Tag {tag} not found in old DICOM dataset. "
                        f"Skipping it."
                    )
                    continue
                for sub_item_new, sub_item_old in zip(
                    new_element[tag], old_element[tag]
                ):
                    replace_tags(sub_item_old, sub_item_new)
                    # print(f"Replacing Sequence {tag}")
            # If tag is marked to be replaced from old DICOM
            elif hasattr(old_element, tag) and getattr(new_element, tag) in [
                PlaceHolderTag.UseOldTagStr,
                PlaceHolderTag.UseOldTagInt,
                PlaceHolderTag.UseOldTagUID,
            ]:
                setattr(new_element, tag, getattr(old_element, tag))
            # Otherwise, if tag is marked to be replaced from old DICOM
            # and it's not present in the old DICOM, skip it
            else:
                warnings.warn(
                    f"Tag {new_element[tag].name} not found in old DICOM dataset. "
                    f"Skipping it."
                )

    replace_tags(empty_new_dicom, old_dicom)

    return empty_new_dicom


def convert_images_to_dicom(
    images: List[Image.Image],
    empty_dicom: pydicom.Dataset = None,
    old_dicom: pydicom.Dataset = None,
    compress_ratio: int = 1,
) -> pydicom.Dataset:
    """
    Converts a list of images to a DICOM dataset, transferring specified tags.

    :param images: List of PIL Image objects.
    :param empty_dicom: An empty DICOM with the tags to transfer to the new dataset.
    :param old_dicom: pydicom Dataset object.
    :param compress_ratio: Optional scalar for resizing.

    :return: New DICOM dataset with specified tags transferred, and image
    """

    if empty_dicom is None:
        empty_dicom = create_empty_dicom(
            dicom_type=DicomTypes.SERIES_ANONYMIZED
        )

    if old_dicom is not None:
        new_dicom = add_tags(empty_dicom, old_dicom)
    else:
        new_dicom = empty_dicom

    data = np.stack(images, axis=0)

    empty_dicom.set_pixel_data(
        data, photometric_interpretation="RGB", bits_stored=8
    )

    if compress_ratio > 1:
        empty_dicom.compress(JPEG2000, j2k_cr=[compress_ratio])

    empty_dicom.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.1"
    empty_dicom.SOPClassUID = "1.2.840.10008.5.1.4.1.1.1"

    # validate
    pydicom.dataset.validate_file_meta(
        empty_dicom.file_meta, enforce_standard=True
    )

    # forces write_like_original=False
    with BytesIO() as output:
        new_dicom.save_as(output, write_like_original=False)
        output.seek(0)
        new_dicom = pydicom.dcmread(output)

    return new_dicom
