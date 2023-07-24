import os
import shutil
from typing import List
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    classification_report,
)
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


class AnalyzeOutput:
    """
    A class to analyze the output CSV file from the text analysis tool.
    Generates confusion matrix and classification metrics for each API.

    Parameters
    ----------
    output_csv: the output csv file to analyze

    Returns
    -------
    None
    """

    # Constants
    CSV_COLUMNS = [
        "Text Type",
        "API Name",
        "File Name",
        "ai_score",
        "human_score",
        "error_message",
    ]
    THRESHOLD = 0.5

    def __init__(self, output_csv: str):
        self.output_csv = output_csv

    def _read_csv(self, csv_file: str):
        """
        Read the csv file
        """
        self.df = pd.read_csv(csv_file)
        return self.df

    def _read_and_sanitize(self, csv_file: str):
        """
        Read and sanitize the data
        """
        df = self._read_csv(csv_file)
        df.columns = self.CSV_COLUMNS
        df = df[df["error_message"].isnull()]
        df = df.reset_index(drop=True)
        return df

    def _calculate_labels(self, df: pd.DataFrame):
        """
        Calculate the labels for the confusion matrix

        Parameters
        ----------
        df: the dataframe to analyze

        Returns
        -------
        y_true: the true labels
        y_pred: the predicted labels
        """
        y_true = [1 if tt == "AI" else 0 for tt in df["Text Type"]]
        y_pred = [1 if float(score) > self.THRESHOLD else 0 for score in df["ai_score"]]

        return y_true, y_pred

    def confusion_matrix(self, csv_file: str):
        """
        Calculate the confusion matrix

        Parameters
        ----------
        csv_file: the csv file to analyze

        Returns
        -------
        None
        """
        df = self._read_and_sanitize(csv_file)
        API = df["API Name"]

        y_true, y_pred = self._calculate_labels(df)

        cm = confusion_matrix(y_true, y_pred)
        print(API[0] + " Confusion Matrix")
        # print(cm)
        print(self._visualize_confusion_matrix(cm, API[0], y_true))

    def _unique_apis(self):
        """
        Get the unique APIs from the output csv

        Returns
        -------
        unique_apis: a list of unique API names
        """
        df = self._read_and_sanitize(self.output_csv)

        grouped = df.groupby("API Name")
        unique_apis = grouped["API Name"].unique()
        for name, group in grouped:
            group.to_csv(f"{name}.csv", index=False)
        return unique_apis

    def _get_visual_labels(self, cm, y_true):
        """
        Get the labels for the confusion matrix based on the number of classes

        Parameters
        ----------
        cm: the confusion matrix
            y_true: the true labels

        Returns
        -------
        df_cm: the confusion matrix as a dataframe
        df_labels: the labels for the confusion matrix as a dataframe
        """
        # Calculate the row-wise sum
        cm_sum = np.sum(cm, axis=1)

        # check if there's only one class in the predictions
        if len(cm) != 1:
            # if the sum of the first row is 0, delete the first row to make the matrix 1x2
            if cm[1].sum() == 0:
                cm = np.delete(cm, 1, 0)
        # if the matrix is 1x1, add a 0 to the second row to make it 1x2
        if len(cm[0]) == 1:
            cm = np.append(cm, [[0]], axis=1)

        #  Calculate the percentage of each cell + add a small number to avoid division by 0
        cm_perc = cm / (cm_sum[:, None] + 1e-10) * 100

        if cm.shape == (1, 2):
            # If there's only one class in the predictions, adjust labels and data accordingly
            single_class = "AI Generated" if y_true[0] == 1 else "Human Written"
            columns = (
                ["AI Generated", "Human Written"]
                if y_true[0] == 1
                else ["Human Written", "AI Generated"]
            )
            labels = [f"{cm_perc[0, 0]:.1f}%", f"{cm_perc[0, 1]:.1f}%"]
            labels = np.asarray(labels).reshape(1, 2)
            df_cm = pd.DataFrame(cm, columns=columns, index=[single_class])
            df_labels = pd.DataFrame(
                labels,
                columns=columns,
                index=[single_class],
            )
        else:
            # If there are two classes, the confusion matrix will be 2x2
            labels = [
                f"{cm_perc[0, 0]:.1f}%",
                f"{cm_perc[0, 1]:.1f}%",
                f"{cm_perc[1, 0]:.1f}%",
                f"{cm_perc[1, 1]:.1f}%",
            ]
            labels = np.asarray(labels).reshape(2, 2)
            df_cm = pd.DataFrame(
                cm,
                columns=["AI Generated", "Human Written"],
                index=["AI Generated", "Human Written"],
            )
            df_labels = pd.DataFrame(
                labels,
                columns=["AI Generated", "Human Written"],
                index=["AI Generated", "Human Written"],
            )
        return df_cm, df_labels

    def _visualize_confusion_matrix(self, cm, api_name: str, y_true):
        """
        Visualize the confusion matrix

        Parameters
        ----------
        cm: the confusion matrix
        api_name: the name of the API
        y_true: the true labels

        Returns
        -------
        df_cm: the confusion matrix as a dataframe
            df_labels: the labels for the confusion matrix as a dataframe
        """

        df_cm, df_labels = self._get_visual_labels(cm, y_true)

        # Visualize the confusion matrix
        plt.figure(figsize=(10, 7))
        sns.heatmap(
            df_cm,
            annot=df_labels,
            fmt="",
        )  # use df_cm as data for heatmap
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.savefig(f"{api_name}_confusion_matrix.png")
        return df_cm, df_labels

    def generate_stats(self, csv_file: str):
        """
        Write the true positive rate, true negative rate, and F1 score to a text file

        Parameters
        ----------
        csv_file: the csv file to analyze

        Returns
        -------
        None

        Writes
        ------
        F1 score
        Precision
        Recall (True Positive Rate)
        Specificity (True Negative Rate)
        False Positive Rate
        Accuracy
        Classification Report
        """
        df = self._read_and_sanitize(csv_file)
        API = df["API Name"][0]

        y_true, y_pred = self._calculate_labels(df)

        f1 = f1_score(y_true, y_pred, zero_division=0)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        accuracy = accuracy_score(y_true, y_pred)
        classification = classification_report(y_true, y_pred, zero_division=0)
        cm = confusion_matrix(y_true, y_pred)

        tnr = cm[0, 0] / (cm[0, 0] + cm[0, 1])
        fp_rate = cm[0, 1] / (cm[0, 0] + cm[0, 1])

        with open(f"{API}_true_rates.txt", "a") as f:
            f.write(f"F1 score: {f1}\n")
            f.write(f"Precision: {precision}\n")
            f.write(f"Recall (True Positive Rate): {recall}\n")
            f.write(f"Specificity (True Negative Rate): {tnr}\n")
            f.write(f"False Positive Rate: {fp_rate}\n")
            f.write(f"Accuracy: {accuracy}\n")
            f.write(f"Classification Report:\n{classification}\n")


def csv_analyzer_main(csv_file: str):
    """
    Main function and entry point for the csv analyzer

    Parameters
    ----------
    csv_file: the csv file to analyze

    Returns
    -------
    None

    Raises
    ------
    FileNotFoundError: if the file is not found
    ValueError: if the file is empty or not a csv file
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"File {csv_file} not found")
    if not csv_file.endswith(".csv"):
        raise ValueError(f"File {csv_file} is not a csv file")
    if os.stat(csv_file).st_size == 0:
        raise ValueError(f"File {csv_file} is empty")

    output_analyzer = AnalyzeOutput(csv_file)
    unique_apis = output_analyzer._unique_apis()
    for API in unique_apis:
        api_with_filetype = API[0] + ".csv"
        output_analyzer.confusion_matrix(api_with_filetype)
        output_analyzer.generate_stats(api_with_filetype)
        file_cleanup(API[0])


def file_cleanup(api_name: str):
    """
    Move the csv files into a folder called output, one for each API

    Parameters
    ----------
    api_name: the name of the API

    Returns
    -------
    None

    """
    for filename in os.listdir():
        if api_name in filename:
            os.makedirs(f"output/{api_name}", exist_ok=True)
            shutil.move(filename, os.path.join(f"output/{api_name}", filename))
