"""
Radstract supports converting NIFTI files of
two different types to labelled images:

- Labelled NIFTI's
- Image NIFTI's
"""

from radstract.data.nifti import (
    convert_nifti_to_image_labels,
    convert_nifti_to_images,
)
from radstract.testdata import Cases, download_case

nii_images, nii_labels = download_case(Cases.ULTRASOUND_NIFTI)

# Quickly get some example labels
images, _ = convert_nifti_to_image_labels(nii_labels)
images[0].save("debug/nifti_creation_labels.png")

# Quickly get some example images
images, _ = convert_nifti_to_images(nii_images)
images[0].save("debug/nifti_creation_images.png")
