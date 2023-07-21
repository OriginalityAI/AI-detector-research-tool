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
        calculate the labels for the confusion matrix
        """
        y_true = [1 if float(score) > self.THRESHOLD else 0 for score in df["ai_score"]]
        y_pred = [1 if tt == "AI" else 0 for tt in df["Text Type"]]
        return y_true, y_pred

    def confusion_matrix(self, csv_file: str):
        """
        Calculate the confusion matrix
        """
        df = self._read_and_sanitize(csv_file)
        API = df["API Name"]

        y_true, y_pred = self._calculate_labels(df)

        cm = confusion_matrix(y_true, y_pred)
        print(API[0] + " Confusion Matrix")
        print(self._visualize_confusion_matrix(cm, API[0]))

    def unique_apis(self):
        """
        Get the unique APIs from the output csv
        """
        df = self._read_and_sanitize(self.output_csv)

        grouped = df.groupby("API Name")
        unique_apis = grouped["API Name"].unique()
        for name, group in grouped:
            group.to_csv(f"{name}.csv", index=False)
        return unique_apis

    def _visualize_confusion_matrix(self, cm, api_name: str):
        """
        Visualize the confusion matrix
        """
        # Calculate the percentage values
        cm_sum_ai = np.sum(cm[0])
        cm_sum_human = np.sum(cm[1])

        if cm_sum_ai == 0:
            cm_sum_ai = 1
        if cm_sum_human == 0:
            cm_sum_human = 1

        cm_perc_ai = cm / cm_sum_ai * 100
        cm_perc_human = cm / cm_sum_human * 100

        # Define the labels with percentage sign and rounded to 1 decimal place
        labels = [
            f"{cm_perc_ai[0, 0]:.1f}%",
            f"{cm_perc_ai[0, 1]:.1f}%",
            f"{cm_perc_human[1, 0]:.1f}%",
            f"{cm_perc_human[1, 1]:.1f}%",
        ]
        labels = np.asarray(labels).reshape(2, 2)

        # Create a DataFrame for the heatmap
        df_cm = pd.DataFrame(
            cm,
            columns=["AI Generated", "Human Written"],
            index=["AI Generated", "Human Written"],
        )

        # Create a DataFrame for the labels
        df_labels = pd.DataFrame(
            labels,
            columns=["AI Generated", "Human Written"],
            index=["AI Generated", "Human Written"],
        )

        # Visualize the confusion matrix
        plt.figure(figsize=(10, 7))
        sns.heatmap(df_cm, annot=df_labels, fmt="")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.savefig(f"{api_name}_confusion_matrix.png")
        return df_cm

    def generate_stats(self, csv_file: str):
        """
        Write the true positive rate, true negative rate, and F1 score to a text file
        """
        df = self._read_and_sanitize(csv_file)
        API = df["API Name"][0]

        y_true, y_pred = self._calculate_labels(df)
        cm = confusion_matrix(y_true, y_pred)

        f1 = f1_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        accuracy = accuracy_score(y_true, y_pred)
        classification = classification_report(y_true, y_pred)
        tp, fp, fn, tn = confusion_matrix(y_true, y_pred).ravel()
        tnr = tn / (tn + fp)

        with open(f"{API}_true_rates.txt", "a") as f:
            f.write(f"F1 score: {f1}\n")
            f.write(f"Precision: {precision}\n")
            f.write(f"Recall (True Positive Rate): {tnr}\n")
            f.write(f"Specificity (True Negative Rate): {recall}\n")
            f.write(f"Accuracy: {accuracy}\n")
            f.write(f"Classification Report:\n{classification}\n")


def csv_analyzer_main(csv_file: str):
    """
    Main function for the csv analyzer
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"File {csv_file} not found")
    if not csv_file.endswith(".csv"):
        raise ValueError(f"File {csv_file} is not a csv file")
    if os.stat(csv_file).st_size == 0:
        raise ValueError(f"File {csv_file} is empty")

    output_analyzer = AnalyzeOutput(csv_file)
    unique_apis = output_analyzer.unique_apis()
    for API in unique_apis:
        api_with_filetype = API[0] + ".csv"
        output_analyzer.confusion_matrix(api_with_filetype)
        output_analyzer.generate_stats(api_with_filetype)
        file_cleanup(API[0])


def file_cleanup(api_name: str):
    """
    Move the csv files into a folder called output, one for each API
    """
    for filename in os.listdir():
        if api_name in filename:
            os.makedirs(f"output/{api_name}", exist_ok=True)
            shutil.move(filename, os.path.join(f"output/{api_name}", filename))
