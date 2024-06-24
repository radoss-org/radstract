"""
Radstract supports converting labelled images to NIFTI files.
"""

from radstract.data.nifti import (
    convert_images_to_nifti_labels,
    convert_nifti_to_image_labels,
)
from radstract.testdata import Cases, download_case

dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

# Quickly get some example labels
images, _ = convert_nifti_to_image_labels(seg_file)

# convert those images to NIFTI
nii = convert_images_to_nifti_labels(images)

# save the NIFTI
nii.save("debug/nifti_creation.nii.gz")
