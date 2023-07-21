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
        print(self._visualize_confusion_matrix(cm))

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

    def _visualize_confusion_matrix(self, cm):
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
        sns.heatmap(df_cm, annot=df_labels, fmt="", cmap="coolwarm")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.show()

    def generate_stats(self, csv_file: str):
        """
        Write the true positive rate, true negative rate, and F1 score to a text file
        """
        df = self._read_and_sanitize(csv_file)
        API = df["API Name"][0]

        y_true, y_pred = self._calculate_labels(df)

        f1 = f1_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        accuracy = accuracy_score(y_true, y_pred)
        classification = classification_report(y_true, y_pred)

        with open(f"{API}_true_rates.txt", "a") as f:
            f.write(f"F1 score: {f1}\n")
            f.write(f"Precision: {precision}\n")
            f.write(f"Recall: {recall}\n")
            f.write(f"Accuracy: {accuracy}\n")
            f.write(f"Classification Report:\n{classification}\n")


def csv_analyzer_main(csv_file: str):
    """
    Main function for the csv analyzer
    """
    output_analyzer = AnalyzeOutput(csv_file)
    unique_apis = output_analyzer.unique_apis()
    for API in unique_apis:
        API += ".csv"
        output_analyzer.confusion_matrix(API[0])
        output_analyzer.generate_stats(API[0])
