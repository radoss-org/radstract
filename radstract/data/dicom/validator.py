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
Validator for DICOM files.

This module provides functions to analyze DICOM files for completeness and
validity.
"""

from typing import Dict


def get_dicom_tag_value(dcm, tag_name: str, default=None):
    """Safely get DICOM tag value with error handling."""
    try:
        return getattr(dcm, tag_name, default)
    except Exception:
        return default


def ohif_validator(dcm, show_present_tags: bool = False) -> Dict:
    """
    Analyze DICOM file for missing tags based on modality and rendering requirements
    of the OHIF viewer.

    Returns a tuple of (requirements_met: bool, analysis: Dict) where analysis contains:
    - present_tags: tags that are present
    - messages: categorized messages with errors, warnings, and info
    """

    analysis = {
        "present_tags": {},
    }

    # Get modality
    modality = get_dicom_tag_value(dcm, "Modality", "UNKNOWN")

    # Common tags for all modalities
    common_tags = {
        "StudyInstanceUID": "Unique identifier for the study",
        "SeriesInstanceUID": "Unique identifier for the series",
        "SOPInstanceUID": "Unique identifier for the object",
        "PhotometricInterpretation": "Color space of the image",
        "Rows": "Image height",
        "Columns": "Image width",
        "PixelRepresentation": "How pixel data should be interpreted",
        "PixelSpacing": "Spacing between pixels",
        "BitsAllocated": "Number of bits allocated for each pixel sample",
        "SOPClassUID": "DICOM service class of the object",
        "InstanceNumber": "Unique identifier for the instance",
        "SeriesNumber": "Unique identifier for the series",
        "PatientID": "Unique identifier for the patient",
    }

    # Rendering tags
    rendering_tags = {
        "RescaleIntercept": "Value used for rescaling pixel values",
        "RescaleSlope": "Value used for rescaling pixel values",
        "WindowCenter": "Windowing parameter for display",
        "WindowWidth": "Windowing parameter for display",
    }

    # Check common tags
    missing_common_tags = []
    for tag, description in common_tags.items():
        value = get_dicom_tag_value(dcm, tag)
        if value is None:
            missing_common_tags.append((tag, description))
        else:
            analysis["present_tags"][tag] = value

    # Check rendering tags
    missing_rendering_tags = []
    for tag, description in rendering_tags.items():
        value = get_dicom_tag_value(dcm, tag)
        if value is None:
            missing_rendering_tags.append((tag, description))
        else:
            analysis["present_tags"][tag] = value

    # Modality-specific tags
    modality_specific_tags = get_modality_specific_tags(modality)
    missing_modality_specific_tags = []
    for tag, description in modality_specific_tags.items():
        value = get_dicom_tag_value(dcm, tag)
        if value is None:
            missing_modality_specific_tags.append((tag, description))
        else:
            analysis["present_tags"][tag] = value

    # Additional checks
    warnings = []
    check_additional_requirements(
        dcm, modality, missing_modality_specific_tags, warnings
    )

    # Add validation results
    messages = {"errors": {}, "warnings": {}, "info": {}}

    # Check for errors (missing common tags are critical)
    if missing_common_tags:
        messages["errors"]["missing_common_tags"] = dict(missing_common_tags)

    # Check for warnings (missing rendering/modality tags)
    if missing_rendering_tags:
        messages["warnings"]["missing_rendering_tags"] = dict(missing_rendering_tags)

    if missing_modality_specific_tags:
        messages["errors"]["missing_modality_specific_tags"] = dict(
            missing_modality_specific_tags
        )

    # Add general warnings
    if warnings:
        messages["warnings"]["general_warnings"] = warnings

    # Add info
    messages["info"]["modality"] = modality
    messages["info"]["present_tags_count"] = len(analysis["present_tags"])

    # Check for UNKNOWN modality as error
    if modality == "UNKNOWN":
        messages["errors"]["unknown_modality"] = "Modality could not be determined"

    if not show_present_tags:
        del analysis["present_tags"]

    # Requirements met if no errors
    analysis["messages"] = messages

    return len(messages["errors"]) == 0, analysis


def get_modality_specific_tags(modality: str) -> Dict[str, str]:
    """Get modality-specific required tags."""

    modality_tags = {
        "US": {  # Ultrasound
            "NumberOfFrames": "Number of frames in a multi-frame image",
        },
        "CT": {  # Computed Tomography
            "ImagePositionPatient": "Position of the image in the patient",
            "ImageOrientationPatient": "Orientation of the image in the patient",
            "InstanceNumber": "Useful for sorting instances",
        },
        "MR": {  # Magnetic Resonance
            "ImagePositionPatient": "Position of the image in the patient",
            "ImageOrientationPatient": "Orientation of the image in the patient",
            "InstanceNumber": "Useful for sorting instances",
        },
        "PT": {  # Positron Tomography
            "RadiopharmaceuticalInformationSequence": "Radiopharmaceutical info",
            "SeriesDate": "Series date",
            "SeriesTime": "Series time",
            "CorrectedImage": "Correction information",
            "Units": "Units of measurement",
            "DecayCorrection": "Decay correction info",
            "AcquisitionDate": "Acquisition date",
            "AcquisitionTime": "Acquisition time",
            "PatientWeight": "Patient weight for SUV calculation",
        },
        "SEG": {  # Segmentation
            "FrameOfReferenceUID": "For handling segmentation layers",
            "ReferencedSeriesSequence": "Referenced series information",
            "SharedFunctionalGroupsSequence": "Shared functional groups",
            "PerFrameFunctionalGroupsSequence": "Per-frame functional groups",
        },
        "RTSTRUCT": {  # Radiotherapy Structure
            "FrameOfReferenceUID": "For handling segmentation layers",
            "ROIContourSequence": "ROI contour information",
            "StructureSetROISequence": "Structure set ROI information",
            "ReferencedFrameOfReferenceSequence": "Referenced frame of reference",
        },
        "SR": {  # Structured Reporting
            "ConceptNameCodeSequence": "Concept name coding",
            "ContentSequence": "Content information",
            "ContentTemplateSequence": "Content template information",
            "CurrentRequestedProcedureEvidenceSequence": "Procedure evidence",
            "CodingSchemeIdentificationSequence": "Coding scheme identification",
        },
    }

    return modality_tags.get(modality, {})


def check_additional_requirements(
    dcm, modality: str, missing_modality_specific_tags: list, warnings: list
):
    """Check additional requirements and add warnings."""

    # Check for sequences that might be missing
    if modality in ["SEG", "RTSTRUCT", "SR"]:
        # Check if sequences exist but are empty
        sequence_tags = [
            "ReferencedSeriesSequence",
            "SharedFunctionalGroupsSequence",
            "PerFrameFunctionalGroupsSequence",
            "ROIContourSequence",
            "StructureSetROISequence",
            "ContentSequence",
        ]

        for tag in sequence_tags:
            value = get_dicom_tag_value(dcm, tag)
            if value is not None and len(value) == 0:
                warnings.append(f"Sequence {tag} exists but is empty")

    # Check for PDF modality
    if hasattr(dcm, "SOPClassUID"):
        sop_class = str(dcm.SOPClassUID)
        if "PDF" in sop_class or "EncapsulatedDocument" in sop_class:
            if not hasattr(dcm, "EncapsulatedDocument"):
                missing_modality_specific_tags.append(
                    ("EncapsulatedDocument", "Contains the PDF document")
                )

    # Check for video modality
    if (
        hasattr(dcm, "NumberOfFrames")
        and get_dicom_tag_value(dcm, "NumberOfFrames", 0) > 1
    ):
        if not hasattr(dcm, "FrameTime"):
            warnings.append("Multi-frame image detected but FrameTime not specified")
