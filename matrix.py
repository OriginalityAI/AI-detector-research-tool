from analyze_output import csv_analyzer_main

input_csv = input("Enter the path to the csv file to analyze: ")
if not input_csv.endswith(".csv"):
    input_csv += ".csv"
try:
    csv_analyzer_main(input_csv)
except Exception as e:
    print(f"An error occurred: {e}")
input("Press enter to exit...")
