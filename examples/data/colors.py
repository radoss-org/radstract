"""
The Colours Module helps to keep the
colours consistent across projects,
As well as some useful helper functions.
"""

from radstract.data.colors import (
    LabelColours,
    change_color,
    fast_check_all_black,
    get_unique_colours,
)
from radstract.data.nifti import convert_nifti_to_image_labels
from radstract.testdata import Cases, download_case

_, seg_file = download_case(Cases.ULTRASOUND_DICOM)

# The LabelColours 1-6 are from ITKSnap
print(LabelColours.LABEL1)

# You can also access this by index
print(LabelColours.get_color_from_index(1))

# You can also check what colour is associated with a label
print(LabelColours.get_colour_key((255, 0, 0)))

# After the first 6, the colours are generated with a random seed
# This means that the colours will be consistent across runs

print(LabelColours.get_color_from_index(10))

# Convert Nifti to Image Labels
image, _ = convert_nifti_to_image_labels(seg_file)
image = image[0]

# We can quickly check if it is all black
assert fast_check_all_black(image) == False

# Get the unique colours in the image
unique_colours = get_unique_colours(image)
print(unique_colours)

# Change the colour of the image
new_image = change_color(image, LabelColours.LABEL1, LabelColours.LABEL2)
