"""
Radstract Dataset Subpackage. For converting between different
datasets structures and formats and working with them.

Note that there is an assumption that all your data is in a
single folder, with the following structure:

```
./input_dir
├── file1.dcm
├── file1.nii.gz
├── file2.dcm
├── file2.nii.gz
```

Each file pair should have the same name, with the DICOM
file ending in .dcm and the NIfTI file ending in .nii.gz.

Currently Supports:
* Huggingface Datasets
* NN-UNet Datasets
* Polygon Datasets

You can also write you own custom save function with:

```python
def save_custom(
    dicom_image: Image.Image,
    seg_image: Image.Image,
    image_dir: str,
    label_dir: str,
    file_name: str,
    file_pair_kwargs: Optional[dict] = None,
):
    pass
```

Example: https://github.com/radoss-org/Radstract/tree/main/examples/dataset
"""
