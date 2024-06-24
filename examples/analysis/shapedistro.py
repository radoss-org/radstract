"""
Shape Distrobutions can be a great way to compare 3D Models.

Find more info from the paper here: https://graphics.stanford.edu/courses/cs468-08-fall/pdf/osada.pdf
"""

import os

from radstract.analysis.shapedistro import (
    ShapeDistroModels,
    generate_comparison_plot,
)
from radstract.testdata import Cases, download_case

*_, dcm1, dcm2, dcm3, dcm4 = download_case(Cases.ULTRASOUND_DICOM_DATASET)

SAVEDIR = "debug"

for folder in ["debug"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

model = ShapeDistroModels.A3

# These NIFTI Files contain Labels. The A3 Model will use these labels
# to generate the shape distribution.
# Group 1 will be colored red, Group 2 will be colored blue.
data = {
    "Group 1": [
        dcm1,
        dcm2,
    ],
    "Group 2": [
        dcm3,
        dcm4,
    ],
}

COLORS = ["red", "blue"]


fig = generate_comparison_plot(
    data,
    COLORS,
    model,
    title=f"{model.upper()} Comparison",
)

fig.savefig(f"{SAVEDIR}/comparison-{model}.png")
