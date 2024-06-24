"""
Radstract supports converting NIFTI Labels into 3D Models.
"""

from radstract.data.models import create_model_from_nifti
from radstract.testdata import Cases, download_case

dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

# Convert NIFTI to 3D Models
model = create_model_from_nifti(seg_file)

# save the model
model.export("debug/nifti-2-model.ply")
