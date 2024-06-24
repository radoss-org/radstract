"""
Radstract has a direct function for converting
DICOM's to NIfTI files.

As well as this, when working with DICOMs and NIFTI Labels,
you can remove frames with no labels with a simple function.
"""

import pydicom

from radstract.data.dicom import convert_dicom_to_images
from radstract.data.multimodal import (convert_dicom_to_nifti,
                                       remove_black_frames)
from radstract.data.nifti import convert_nifti_to_image_labels
from radstract.testdata import Cases, download_case

dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

# Convert DICOM to NIFTI
dcm = pydicom.dcmread(dcm_file)

dicom_images = convert_dicom_to_images(dcm)
nifti_images, _ = convert_nifti_to_image_labels(seg_file)

# Remove black frames
dicom, nifti = remove_black_frames(dicom_images, nifti_images)


nifti = convert_dicom_to_nifti(dcm)

nifti.save("debug/dicom-2-nifti.nii.gz")
