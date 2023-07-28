import csv
import math
import os
import pandas as pd
from typing import Any, Dict, List

import requests

from api_endpoints import API_ENDPOINTS

"""
This program takes in a directory of text files and runs them through the selected APIs to determine if the text is human or AI generated.
"""


class TextAnalyzer:
    """
    class that handles the text analysis

    Parameters
    ----------
    output_csv: the output csv file to write the results to
    api_info: the API settings
    api_name: the name of the API
    writer_organization_id: the writer organization ID for the Writer.com API
    copyleaks_scan_id: the Copyleaks scan ID for the Copyleaks API

    Returns
    -------
    None
    """

    def __init__(
        self,
        output_csv: str,
        api_info: Dict[str, Dict[str, Any]],
        api_name: str,
        writer_organization_id=None,
        copyleaks_scan_id=None,
    ) -> None:
        self.output_csv = output_csv
        self.api_info = api_info
        self.api_name = api_name
        self.writer_organization_id = writer_organization_id
        self.copyleaks_scan_id = copyleaks_scan_id

    def _get_endpoint(self, endpoint):
        """
        Replace the writer_organization_id and copyleaks_scan_id in the endpoint with the actual values

        Parameters
        ----------
        endpoint: the endpoint to replace the values in

        Returns
        -------
        endpoint: The endpoint with the values replaced
        """
        if "{writer_organization_id}" in endpoint:
            return endpoint.format(writer_organization_id=self.writer_organization_id)
        if "{copyleaks_scan_id}" in endpoint:
            return endpoint.format(copyleaks_scan_id=self.copyleaks_scan_id)

        return endpoint

    def _handle_data(self, data, keys):
        """
        Extract the values from the data that correspond to the keys provided

        Parameters
        ----------
        data: the data to extract the values from
        keys: the keys to extract the values for

        Returns
        -------
        row: the values extracted from the data
        """
        row = []
        try:
            # if the keys are a list, then loop through the data and extract the values that correspond to the keys
            if isinstance(keys, list):
                for item in data:
                    for key, value in item.items():
                        if key in keys:
                            row.append(value)
            else:
                # if the keys are a dictionary, then loop through the data and extract the values that correspond to the keys
                for key, value in keys.items():
                    if isinstance(data.get(key), dict):
                        row.extend(self._handle_data(data[key], value))
                    elif isinstance(data.get(key), list):
                        for sub_dict in data[key]:
                            for sub_key, sub_value in sub_dict.items():
                                if sub_key in value:
                                    row.append(sub_value)
                    else:
                        row.append(data.get(key))
            return row
        except Exception as e:
            print(f"An error occurred: {e} check the API response format in api_endpoints.py")
            return exit()

    def _extract_values(
        self,
        data: Dict[str, Dict[str, Any]],
        keys: Dict[str, List[str]],
    ) -> List[Any]:
        """
        Extract the values from the data that correspond to the keys provided needed to do it this way to avoid type errors
        """
        return self._handle_data(data, keys)

    def _write_error(self, text_type, row, index, response, output_csv, api_name):
        with open(output_csv, "a", newline="", encoding="UTF-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    text_type,
                    api_name,
                    f"{row['dataset']}-{index}",
                    "Error",
                    "Error",
                    f"Error: {response.text}",
                ]
            )

    def process_files(self, input_path, text_type, is_csv=False):
        """
        Main function that processes the files in the directory using the API and writes the results to the CSV file

        Parameters
        ----------
        directory: the directory to process the files in
        text_type: the type of text to process (AI or Human)

        Returns
        -------
        None
        """
        api_post = self.api_info["post_parameters"]
        api_response = self.api_info["response"]["200"]
        api_name = self.api_name
        text_key = api_post.get("text_key", "content")
        output_csv = self.output_csv
        endpoint = self._get_endpoint(api_post["endpoint"])

        if "headers" in api_post:
            headers = api_post["headers"]
        else:
            headers = {}

        body = api_post["body"]

        try:
            if is_csv:
                df = pd.read_csv(input_path)

                for index, row in df.iterrows():
                    text_type = "Human" if "human" in row["dataset"].lower() else "AI"
                    text = row["text"]
                    body[text_key] = text
                    parameters = body.copy()

                    try:
                        del parameters["API_KEY_POINTER"]
                    except KeyError:
                        pass

                    for key, value in parameters.items():
                        if isinstance(value, float):
                            if math.isinf(value) or math.isnan(value) or value > 1.7e308:
                                print(
                                    f"⚠️  Warning: The value for {key} is not JSON compliant. Replacing with a default value."
                                )
                                parameters[key] = 0.0

                    try:
                        response = requests.post(endpoint, headers=headers, json=parameters, timeout=60)
                    except ValueError as e:
                        print(f"A ValueError occurred: {e}")
                        self._write_error(text_type, row, index, e, output_csv, api_name)
                        continue

                    if response.status_code != 200:
                        print(f"❌ Error: {response.text}")
                        self._write_error(text_type, row, index, response, output_csv, api_name)
                        continue

                    data = response.json()

                    row = [text_type, api_name, f"{row['dataset']}-{index}", row["dataset"]] + self._extract_values(
                        data, api_response
                    )

                    with open(output_csv, "a", newline="", encoding="UTF-8") as file:
                        writer = csv.writer(file)
                        writer.writerow(row)

                    print(f"✅ CSV row {index} processed successfully using {api_name}")

            else:
                for filename in os.listdir(input_path):
                    if filename.endswith(".txt"):
                        with open(os.path.join(input_path, filename), "r", encoding="UTF-8") as f:
                            text = f.read()

                        body[text_key] = text
                        parameters = body.copy()

                        try:
                            del parameters["API_KEY_POINTER"]
                        except KeyError:
                            pass

                        response = requests.post(endpoint, headers=headers, json=parameters, timeout=60)

                        if response.status_code != 200:
                            print(f"❌ Error: {response.text}")
                            with open(output_csv, "a", newline="", encoding="UTF-8") as file:
                                writer = csv.writer(file)
                                writer.writerow(
                                    [text_type, api_name, filename, "Error", "Error", f"Error: {response.text}"]
                                )
                            continue

                        data = response.json()
                        row = [text_type, api_name, filename] + self._extract_values(data, api_response)

                        with open(output_csv, "a", newline="", encoding="UTF-8") as file:
                            writer = csv.writer(file)
                            writer.writerow(row)

                        print(f"✅ File {filename} processed successfully using {api_name}")
        except KeyError as e:
            print(f"❌ Error: missing {e} key, check the CSV format in the README.md file")
            return exit()

    def _get_nested_value(self, dictionary, keys):
        """
        Retrieve the value from a nested dictionary using the keys provided

        Parameters
        ----------
        dictionary: the dictionary to retrieve the value from
        keys: the keys to retrieve the value for

        Returns
        -------
        dictionary: A dictionary containing the value retrieved from the nested dictionary
        """
        for key in keys:
            if isinstance(dictionary, list):
                dictionary = [
                    sub_dict.get(key, None) if isinstance(sub_dict, dict) else None for sub_dict in dictionary
                ]
            else:
                dictionary = dictionary.get(key, None)
        return dictionary


def set_headers(output_csv: str, file_type: str) -> None:
    """
    Set the initial headers for the CSV file

    Parameters
    ----------
    output_csv: the output CSV file to write the headers to

    Returns
    -------
    None
    """
    if file_type == "csv":
        init_row = [
            "Text Type",
            "API Name",
            "File Name",
            "Dataset",
            "ai_score",
            "human_score",
            "Error_message",
        ]
    else:
        init_row = [
            "Text Type",
            "API Name",
            "File Name",
            "ai_score",
            "human_score",
            "Error_message",
        ]

    with open(output_csv, "a", newline="", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(init_row)


def api_constructor(selected_endpoints):
    """
    Construct the API settings dictionary using the selected endpoints and API keys

    Parameters
    ----------
    selected_endpoints: the selected endpoints to use

    Returns
    -------
    api_settings: the API settings dictionary
    """
    # Initialize an empty dictionary to hold API settings
    api_settings = {}

    # Iterate over the selected endpoints
    for api_name, api_key in selected_endpoints.items():
        # Get the API's settings from the master dictionary
        api_info = API_ENDPOINTS[api_name]

        # Update the API key in the post_parameters dictionary
        key_location = api_info["post_parameters"]["API_KEY_POINTER"]["location"]
        if key_location == "headers":
            api_info["post_parameters"]["headers"][api_info["post_parameters"]["API_KEY_POINTER"]["key_name"]] = (
                api_info["post_parameters"]["API_KEY_POINTER"]["value"] + api_key
            )
        elif key_location == "body":
            api_info["post_parameters"]["body"][api_info["post_parameters"]["API_KEY_POINTER"]["key_name"]] = api_key
        del api_info["post_parameters"]["API_KEY_POINTER"]
        # Add the modified API info to the api_settings dictionary
        api_settings[api_name] = api_info
    return api_settings


def get_input():
    """
    Get the user input for the API endpoints, API keys, and directories

    Parameters
    ----------
    None

    Returns
    -------
    api_settings: the API settings dictionary
    ai_directory: the directory path for AI text files
    human_directory: the directory path for human text files
    output_csv: the output CSV file path
    writer_organization_id: the writer organization ID for the Writer.com API
    copyleaks_scan_id: the Copyleaks scan ID for the Copyleaks API
    """
    writer_organization_id = None
    copyleaks_scan_id = None
    selected_endpoints = {}

    for api_name in API_ENDPOINTS:
        is_selected = input(f"Type Y/N to select {api_name} API: ")
        if is_selected.upper() == "Y":
            if api_name == "Writer.com":
                writer_organization_id = input("Please enter your Organization ID: ")
            elif api_name == "Copyleaks":
                copyleaks_scan_id = input("Please enter a Copyleaks scan ID: ")
            api_info = input("Please enter your API key: ")
            if api_info is None:
                print("Invalid API Key")
                break
            selected_endpoints[api_name] = api_info

    api_settings = api_constructor(selected_endpoints)

    ai_directory = input("Enter the directory path for AI text files: ")
    human_directory = input("Enter the directory path for human text files: ")
    input_csv = input("Enter the input CSV file path: ")
    output_csv = input("Enter the output CSV file name: ")

    if output_csv is None:
        print("Invalid output CSV file path")
        exit(1)
    if output_csv.endswith(".csv"):
        if input_csv.endswith(".csv"):
            set_headers(output_csv, "csv")
        else:
            set_headers(output_csv, "txt")
    else:
        output_csv += ".csv"
        if input_csv.endswith(".csv"):
            set_headers(output_csv, "csv")
        else:
            set_headers(output_csv, "txt")

    return [
        api_settings,
        ai_directory,
        human_directory,
        output_csv,
        writer_organization_id,
        copyleaks_scan_id,
        input_csv,
    ]


def text_analyzer_main():
    """
    main function that runs the text analyzer

    Parameters
    ----------
    None

    Returns
    -------
    output_csv: the output CSV file path
    """
    print("Welcome to the API Interaction Program. Please check the following API endpoints you wish to use: ")
    (
        api_settings,
        ai_directory,
        human_directory,
        output_csv,
        writer_organization_id,
        copyleaks_scan_id,
        input_csv,
    ) = get_input()

    for api_name, api in api_settings.items():
        text_analyzer = TextAnalyzer(output_csv, api, api_name, writer_organization_id, copyleaks_scan_id)
        if input_csv != "":
            text_analyzer.process_files(input_csv, "", True)
        if ai_directory != "":
            print(f"🤖 Processing AI files using {api_name}...")
            text_analyzer.process_files(ai_directory, "AI")
        if human_directory != "":
            print(f"👨‍💻 Processing human files using {api_name}...")
            text_analyzer.process_files(human_directory, "Human")
    return output_csv
