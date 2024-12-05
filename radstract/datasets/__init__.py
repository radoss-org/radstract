# Copyright 2024 Adam McArthur
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
