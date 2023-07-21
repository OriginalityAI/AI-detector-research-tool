from text_analyzer import text_analyzer_main
from analyze_output import csv_analyzer_main


# output_csv = text_analyzer_main()
output_csv = "test_output.csv"
graphs = input("Would you like to generate a confusion matrix? (y/n): ")
if graphs == "y":
    csv_analyzer_main(output_csv)
