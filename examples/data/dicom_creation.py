"""
Radstract supportd creating DICOM files from images.

This is an experimental feature, and is not recommended for production use.
"""

from PIL import Image

from radstract.data.dicom import convert_images_to_dicom

# create random noise image
image = Image.new("RGB", (512, 512))

images = [image, image]

# convert images to dicom
dcm = convert_images_to_dicom(images)

# save dicom
dcm.save_as("debug/dicom_creation.dcm")
