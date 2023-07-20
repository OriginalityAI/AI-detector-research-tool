import pandas as pd
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from text_analyzer import text_analyzer_main


class AnalyzeOutput:
    def __init__(self, output_csv: str):
        self.output_csv = output_csv

    def _read_csv(self):
        self.df = pd.read_csv(self.output_csv)
        return self.df

    def confusion_matrix(self):
        csv = self._read_csv()
        ai_score = csv["ai_score"]
        rounded_ai_score = []
        for i in range(len(ai_score)):
            if ai_score[i] > 0.5:
                rounded_ai_score.append(1)
            else:
                rounded_ai_score.append(0)

    def unique_apis(self):
        csv = self._read_csv()
        csv.columns = [
            "Text Type",
            "API Name",
            "File Name",
            "ai_score",
            "human_score",
            "error_message",
        ]
        grouped = csv.groupby("Text Type")
        print(grouped)


def csv_analyzer_main(csv_file: str):
    output_analyzer = AnalyzeOutput(csv_file)
    print(output_analyzer.unique_apis())
