import os
from unittest.mock import patch

from radstract.datasets.utils import DataSplit, decide_data_split


def test_decide_data_split():
    with patch("numpy.random.rand") as mock_rand:
        dataset_dir = "path/to/dataset"

        # Test for train split
        mock_rand.return_value = 0.2
        data_split = DataSplit(pc_train=0.3, pc_val=0.4, pc_test=0.3)
        image_dir, label_dir = decide_data_split(dataset_dir, data_split)
        assert image_dir == os.path.join(dataset_dir, "images/train")
        assert label_dir == os.path.join(dataset_dir, "labels/train")

        data_split = (0.3, 0.4)
        image_dir, label_dir = decide_data_split(dataset_dir, data_split)
        assert image_dir == os.path.join(dataset_dir, "images/train")
        assert label_dir == os.path.join(dataset_dir, "labels/train")

        # # Test for validation split
        mock_rand.return_value = 0.3
        image_dir, label_dir = decide_data_split(dataset_dir, data_split)
        assert image_dir == os.path.join(dataset_dir, "images/val")
        assert label_dir == os.path.join(dataset_dir, "labels/val")

        # # Test for test split
        mock_rand.return_value = 0.8
        image_dir, label_dir = decide_data_split(dataset_dir, data_split)
        assert image_dir == os.path.join(dataset_dir, "images/test")
        assert label_dir == os.path.join(dataset_dir, "labels/test")
