## A simple visualizer for the GaiaML project.
# This module provides basic visualization capabilities for the project.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_data(df, x_col, y_col, title="Data Visualization", xlabel=None, ylabel=None):
    """
    Plots the data from a DataFrame.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data to plot.
        x_col (str): The name of the column to use for the x-axis.
        y_col (str): The name of the column to use for the y-axis.
        title (str): The title of the plot.
        xlabel (str): The label for the x-axis. If None, uses x_col.
        ylabel (str): The label for the y-axis. If None, uses y_col.
    """
    plt.figure(figsize=(10, 6))
    plt.scatter(df[x_col], df[y_col], alpha=0.5)
    plt.title(title)
    plt.xlabel(xlabel if xlabel else x_col)
    plt.ylabel(ylabel if ylabel else y_col)
    plt.grid(True)
    plt.show()
