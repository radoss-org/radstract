"""
Radstract has a direct function for converting
DICOM's to NIfTI files.

As well as this, when working with DICOMs and NIFTI Labels,
you can remove frames with no labels with a simple function.
"""

import pydicom

from radstract.data.dicom import convert_dicom_to_images
from radstract.testdata import Cases, download_case

dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

# Convert DICOM to NIFTI
dcm = pydicom.dcmread(dcm_file)

dicom_images = convert_dicom_to_images(dcm)

# save the first image
dicom_images[0].save("debug/dicom-2-image.png")
