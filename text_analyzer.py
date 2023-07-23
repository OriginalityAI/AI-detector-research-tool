import requests
import os
import csv
from typing import Dict, Any, List
from api_endpoints import API_ENDPOINTS

"""
This program takes in a directory of text files and runs them through the selected APIs to determine if the text is human or AI generated.
"""


class TextAnalyzer:
    """
    class that handles the text analysis
    """

    def __init__(
        self,
        output_csv: str,
        api_info: Dict[str, Dict[str, Any]],
        api_name: str,
        writer_organization_id=None,
        copyLeaks_scan_id=None,
    ) -> None:
        self.output_csv = output_csv
        self.api_info = api_info
        self.api_name = api_name
        self.writer_organization_id = writer_organization_id
        self.copyLeaks_scan_id = copyLeaks_scan_id

    def _get_endpoint(self, endpoint):
        """
        replace the writer_organization_id and copyLeaks_scan_id in the endpoint with the actual values
        """
        if "{writer_organization_id}" in endpoint:
            return endpoint.format(writer_organization_id=self.writer_organization_id)
        elif "{copyLeaks_scan_id}" in endpoint:
            return endpoint.format(copyLeaks_scan_id=self.copyLeaks_scan_id)
        else:
            return endpoint

    def _handle_data(self, data, keys):
        """
        extract the values from the data that correspond to the keys provided
        """
        row = []
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

    def _extract_values(
        self,
        data: Dict[str, Dict[str, Any]],
        keys: Dict[str, List[str]],
    ) -> List[Any]:
        return self._handle_data(data, keys)

    """
    extract the values from the data that correspond to the keys provided
    """

    def _process_files(self, directory, text_type):
        """
        main function that processes the files in the directory using the API and writes the results to the CSV file
        """
        api_post = self.api_info["post_parameters"]
        api_response = self.api_info["response"]["200"]
        api_name = self.api_name
        text_key = api_post.get("text_key", "content")
        output_csv = self.output_csv
        endpoint = self._get_endpoint(api_post["endpoint"])

        # set the headers for the CSV file
        if "headers" in api_post:
            headers = api_post["headers"]
        else:
            headers = {}

        body = api_post["body"]

        # loop through the files in the directory
        for filename in os.listdir(directory):
            # if the file is a text file
            if filename.endswith(".txt"):
                # open the file and read the text
                with open(os.path.join(directory, filename), "r") as f:
                    text = f.read()
                    body[text_key] = text
                    parameters = body.copy()
                    try:
                        del parameters["API_KEY_POINTER"]
                    except KeyError:
                        pass

                    response = requests.post(endpoint, headers=headers, json=parameters)

                    # scan the text using the API to check if it is human or AI generated
                    if response.status_code != 200:
                        print(f"❌ Error: {response.text}")
                        with open(output_csv, "a", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow(
                                [
                                    text_type,
                                    api_name,
                                    filename,
                                    "Error",
                                    "Error",
                                    response.text,
                                ]
                            )
                        continue

                    data = response.json()

                    # create the row to be written to the CSV file
                    row = [text_type, api_name, filename] + self._extract_values(
                        data, api_response
                    )

                    # write the row to the CSV file
                    with open(output_csv, "a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(row)

                    print(f"✅ File {filename} processed successfully using {api_name}")

    def get_nested_value(self, dictionary, keys):
        """
        retrieve the value from a nested dictionary using the keys provided
        """
        for key in keys:
            if isinstance(dictionary, list):
                dictionary = [
                    sub_dict.get(key, None) if isinstance(sub_dict, dict) else None
                    for sub_dict in dictionary
                ]
            else:
                dictionary = dictionary.get(key, None)
        return dictionary


def set_headers(output_csv: str) -> None:
    """
    set the initial headers for the CSV file
    """
    init_row = [
        "Text Type",
        "API Name",
        "File Name",
        "ai_score",
        "human_score",
        "Error_message",
    ]
    with open(output_csv, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(init_row)


def api_constructor(selected_endpoints):
    """
    construct the API settings dictionary
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
            api_info["post_parameters"]["headers"][
                api_info["post_parameters"]["API_KEY_POINTER"]["key_name"]
            ] = api_key
            api_info["post_parameters"]["API_KEY_POINTER"]["value"] = api_key
        elif key_location == "body":
            api_info["post_parameters"]["body"][
                api_info["post_parameters"]["API_KEY_POINTER"]["key_name"]
            ] = api_key
        del api_info["post_parameters"]["API_KEY_POINTER"]
        # Add the modified API info to the api_settings dictionary
        api_settings[api_name] = api_info

    return api_settings


def get_input():
    """
    get the user input for the API endpoints, API keys, and directories
    """
    writer_organization_id = None
    copyLeaks_scan_id = None
    selected_endpoints = {}

    for api_name in API_ENDPOINTS:
        is_selected = input(f"Type Y/N to select {api_name} API: ")
        if is_selected.upper() == "Y":
            if api_name == "Writer.com":
                writer_organization_id = input("Please enter your Organization ID: ")
            elif api_name == "Copyleaks":
                copyLeaks_scan_id = input("Please enter your Copyleaks scan ID: ")
            api_info = input("Please enter your API key: ")
            if api_info is None:
                print("Invalid API Key")
                break
            selected_endpoints[api_name] = api_info

    api_settings = api_constructor(selected_endpoints)

    ai_directory = input("Enter the directory path for AI text files: ")

    human_directory = input("Enter the directory path for human text files: ")

    output_csv = input("Enter the output CSV file path: ")
    if output_csv is None:
        print("Invalid output CSV file path")
        exit(1)
    if output_csv.endswith(".csv"):
        set_headers(output_csv)
    else:
        output_csv += ".csv"
        set_headers(output_csv)

    return [
        api_settings,
        ai_directory,
        human_directory,
        output_csv,
        writer_organization_id,
        copyLeaks_scan_id,
    ]


def text_analyzer_main():
    """
    main function that runs the text analyzer
    """
    print(
        "Welcome to the API Interaction Program. Please check the following API endpoints you wish to use: "
    )
    (
        api_settings,
        ai_directory,
        human_directory,
        output_csv,
        writer_organization_id,
        copyLeaks_scan_id,
    ) = get_input()

    for api_name, api in api_settings.items():
        text_analyzer = TextAnalyzer(
            output_csv, api, api_name, writer_organization_id, copyLeaks_scan_id
        )
        if ai_directory != "":
            print(f"🤖 Processing AI files using {api_name}...")
            text_analyzer._process_files(ai_directory, "AI")
        if human_directory != "":
            print(f"👨‍💻 Processing human files using {api_name}...")
            text_analyzer._process_files(human_directory, "Human")
    return output_csv
