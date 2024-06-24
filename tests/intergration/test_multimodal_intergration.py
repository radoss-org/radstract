import tempfile

import nibabel as nib
import numpy as np
import pydicom

from radstract.data.multimodal import convert_dicom_to_nifti
from radstract.data.nifti import convert_nifti_to_images


def test_convert_dicom_to_nifti(dicom_nifti_data):
    dcm_file, nii_file = dicom_nifti_data
    dcm = pydicom.dcmread(dcm_file)
    nifti = nib.load(nii_file)

    dcm_nifti = convert_dicom_to_nifti(dcm)
    # create a temp file to save the nifti
    with tempfile.NamedTemporaryFile(suffix=".nii.gz") as temp_nifti:
        dcm_nifti.save(temp_nifti.name)
        dcm_nifti = nib.load(temp_nifti.name)

        # convert both niftis to images
        nifti_imgs, _ = convert_nifti_to_images(nifti)
        dcm_nifti_imgs, _ = convert_nifti_to_images(dcm_nifti)

        nifti_img = nifti_imgs[0]
        dcm_nifti_img = dcm_nifti_imgs[0]

        # compare if the np arrays are equal
        assert np.array_equal(nifti_img, dcm_nifti_img)
