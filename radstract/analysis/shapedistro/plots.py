"""
Code for working with Shape Distributions.

Example: https://github.com/radoss-org/Radstract/tree/main/examples/analysis/shapedistro.py
"""

import logging
import os
from collections import defaultdict
from typing import List, Tuple, Union

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from nibabel import Nifti1Image

from radstract.data.models import create_model_from_nifti

from .models.common import ShapeDistroModels, generate_distribution


def rolling_average(a: np.ndarray, window_size: int) -> np.ndarray:
    """
    Calculate the moving average of a given array.

    :param a: Array of numbers
    :param window_size: Window size for the moving average

    :return: Array of the moving average
    """

    out = np.convolve(a, np.ones(window_size), "valid") / window_size

    return out


def calculate_average(
    niftis: List[Union[str, Nifti1Image]],
    model: ShapeDistroModels,
    window_size: int = 5,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate the average histogram for a list of NIFTI
    files using a given model.

    :param niftis: List of NIFTI files to be processed
    :param model: The model to be used for processing
    :param cache: If true, cache the processed data

    :return: average_bin_centers, average_hist
    """

    # defaultdict for accumulating sum and count for each bin_center
    sum_dict = defaultdict(float)
    count_dict = defaultdict(int)

    for nifti in niftis:
        # Get bins and histogram for the current NIFTI file
        ply_file = create_model_from_nifti(nifti)
        bin_centers, hist = generate_distribution(ply_file, model)

        # Update the sum_dict and count_dict
        for i, bin_center in enumerate(bin_centers):
            sum_dict[bin_center] += hist[i]
            count_dict[bin_center] += 1

    # Calculate the average histogram
    average_bin_centers = sorted(sum_dict.keys())
    average_hist = [sum_dict[x] / count_dict[x] for x in average_bin_centers]

    # Apply rolling average on the calculated average histogram
    average_hist_rolled = rolling_average(average_hist, window_size)

    # Since the rolling average "shrinks" the array,
    # adjust bin centers accordingly
    trim_length = len(average_bin_centers) - len(average_hist_rolled)
    start_index = int(trim_length / 2)
    end_index = -int(
        (trim_length + 1) / 2
    )  # Adjustment made here to correctly trim
    trimmed_average_bin_centers = average_bin_centers[start_index:end_index]

    return np.array(trimmed_average_bin_centers), np.array(average_hist_rolled)


def generate_comparison_plot(
    niftis: List[Union[str, Nifti1Image]],
    colors: List[str],
    model: ShapeDistroModels,
    title: str = "Comparison",
    extra_plots: dict = None,
) -> plt.figure:
    """
    Assuming niftis is a list of lists, with each list
    being one colour on a plot, generate a plot of the
    data in the niftis.

    :param niftis: List of NIFTI files to be processed
    :param colors: List of colours for the plot
    :param model: The model to be used for processing
    :param title: Title of the plot
    :param extra_plots: Extra plots to be included in the plot

    :return: The plot

    :raises ValueError: If nifti_list is empty or if a file does not exist
    """

    plt.figure()

    for n, (key, nifti_list) in enumerate(niftis.items()):
        if len(nifti_list) == 0:
            raise ValueError("nifti_list cannot be empty")

        for nifti in nifti_list:
            if not os.path.exists(nifti):
                raise ValueError(f"File {nifti} does not exist")

            ply_file = create_model_from_nifti(nifti)
            bin_centers, hist = generate_distribution(ply_file, model)

            # Save this to cache file
            plt.plot(
                bin_centers,
                hist,
                color=colors[n],
                linewidth=1,
                alpha=0.7,
            )

        logging.info(f"Completed {key}")

    n = len(niftis)

    extra_legend_elements = []

    if extra_plots is not None:
        for i, (label, (x, y)) in enumerate(extra_plots.items()):
            plt.plot(x, y, color=colors[n + i], linewidth=3)

            extra_legend_elements.append(
                Line2D([0], [0], color=colors[n + i], lw=4, label=label)
            )

    legend_elements = [
        Line2D([0], [0], color=colors[n], lw=4, label=key)
        for n, (key, _) in enumerate(niftis.items())
    ]

    legend_elements.extend(extra_legend_elements)
    plt.legend(handles=legend_elements)
    plt.title(f"{title}")

    # Remove ticks
    plt.xticks([])
    plt.yticks([])

    # return the figure
    return plt.gcf()


def get_plot_data(
    niftis: List[Union[str, Nifti1Image]], model: ShapeDistroModels
) -> dict:
    """
    Get the plot data for a list of NIFTI files using a given model.

    :param niftis: List of NIFTI files to be processed
    :param model: The model to be used for processing

    :return: The plot data

    :raises ValueError: If nifti_list is empty or if a file does not exist
    """
    data = {}
    for key, nifti_list in niftis.items():
        if len(nifti_list) == 0:
            raise ValueError("nifti_list cannot be empty")

        for nifti in nifti_list:
            if not os.path.exists(nifti):
                raise ValueError(f"File {nifti} does not exist")

            ply_file = create_model_from_nifti(nifti)
            bin_centers, hist = generate_distribution(ply_file, model)

        data.setdefault(key, []).append((bin_centers, hist))

    return data
