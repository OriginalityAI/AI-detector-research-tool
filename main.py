from text_analyzer import text_analyzer_main
from analyze_output import csv_analyzer_main


output_csv = text_analyzer_main()
graphs = input("Would you like to generate a confusion matrix? (y/n): ")
if graphs == "y":
    try:
        csv_analyzer_main(output_csv)
    except Exception as e:
        print(f"An error occurred: {e}")
input("Press enter to exit...")
