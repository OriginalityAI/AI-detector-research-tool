from typing import List
import pandas as pd
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


class AnalyzeOutput:
    def __init__(self, output_csv: str):
        self.output_csv = output_csv

    def _read_csv(self, csv_file: str):
        self.df = pd.read_csv(csv_file)
        return self.df

    def _sanitize(self, csv_file: str):
        df = self._read_csv(csv_file)
        df.columns = [
            "Text Type",
            "API Name",
            "File Name",
            "ai_score",
            "human_score",
            "error_message",
        ]
        df = df.dropna()
        df = df.drop_duplicates()
        df = df[df["error_message"].isnull()]
        df.to_csv(csv_file, index=False)
        return df

    def _sanitize_data(self, df: pd.DataFrame):
        df.columns = [
            "Text Type",
            "API Name",
            "File Name",
            "ai_score",
            "human_score",
            "error_message",
        ]
        df = df[df["error_message"].isnull()]
        df = df.reset_index(drop=True)
        return df

    def _calculate_labels(self, df: pd.DataFrame):
        y_true = []
        y_pred = []
        for i in range(len(df["Text Type"])):
            if df["Text Type"][i] == "AI":
                y_pred.append(1)
            else:
                y_pred.append(0)
        for i in range(len(df["ai_score"])):
            if float(df["ai_score"][i]) > 0.5:
                y_true.append(1)
            else:
                y_true.append(0)
        return y_true, y_pred

    def _visualize_confusion_matrix(self, cm):
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

    def confusion_matrix(self, csv_file: str):
        df = self._read_csv(csv_file)
        df = self._sanitize_data(df)
        API = df["API Name"]

        y_true, y_pred = self._calculate_labels(df)

        cm = confusion_matrix(y_true, y_pred)
        print(API[0] + " Confusion Matrix")
        print(self._visualize_confusion_matrix(cm))

    def unique_apis(self):
        csv = self._read_csv(self.output_csv)
        csv.columns = [
            "Text Type",
            "API Name",
            "File Name",
            "ai_score",
            "human_score",
            "error_message",
        ]
        grouped = csv.groupby("API Name")
        unique_apis = grouped["API Name"].unique()
        for name, group in grouped:
            group.to_csv(f"{name}.csv", index=False)
        return unique_apis


def csv_analyzer_main(csv_file: str):
    output_analyzer = AnalyzeOutput(csv_file)
    unique_apis = output_analyzer.unique_apis()
    for API in unique_apis:
        API += ".csv"
        output_analyzer.confusion_matrix(API[0])
