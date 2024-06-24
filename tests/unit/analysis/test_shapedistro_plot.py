import os

import numpy as np

from radstract.analysis.shapedistro.models import ShapeDistroModels
from radstract.analysis.shapedistro.plots import (
    calculate_average,
    generate_comparison_plot,
    get_plot_data,
    rolling_average,
)


def test_rolling_average():
    # Prepare test data
    a = np.array([1, 2, 3, 4, 5])
    window_size = 3

    # Call the function
    result = rolling_average(a, window_size)

    # Assert the expected results
    assert isinstance(result, np.ndarray)
    assert len(result) == len(a) - window_size + 1
    assert np.allclose(result, np.array([2, 3, 4]))


def test_calculate_average(ultrasound_nifti_labels):
    # Prepare test data
    niftis = [ultrasound_nifti_labels, ultrasound_nifti_labels]
    model = ShapeDistroModels.A3

    # Call the function
    average_bin_centers, average_hist = calculate_average(niftis, model)

    # Assert the expected results
    assert isinstance(average_bin_centers, np.ndarray)
    assert isinstance(average_hist, np.ndarray)


def test_generate_comparison_plot(ultrasound_nifti_labels):
    # Prepare test data
    niftis = {
        "group1": [ultrasound_nifti_labels, ultrasound_nifti_labels],
        "group2": [ultrasound_nifti_labels, ultrasound_nifti_labels],
    }
    colors = ["red", "blue"]
    model = ShapeDistroModels.A3

    # Call the function
    fig = generate_comparison_plot(niftis, colors, model)

    # Assert the expected results
    assert fig is not None


def test_get_plot_data(ultrasound_nifti_labels):
    # Prepare test data
    niftis = {
        "group1": [ultrasound_nifti_labels, ultrasound_nifti_labels],
        "group2": [ultrasound_nifti_labels, ultrasound_nifti_labels],
    }
    model = ShapeDistroModels.A3

    # Call the function
    data = get_plot_data(niftis, model)

    # Assert the expected results
    assert isinstance(data, dict)
    assert len(data) == len(niftis)
    for group, plot_data in data.items():
        assert isinstance(plot_data, list)
        for bin_centers, hist in plot_data:
            assert isinstance(bin_centers, np.ndarray)
            assert isinstance(hist, np.ndarray)
            assert len(bin_centers) == len(hist)
