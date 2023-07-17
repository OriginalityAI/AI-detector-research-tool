import requests
import json
import os
import csv


output_csv = "output.csv"


def process_files(directory, text_type, api_name, api_info):
    print(f"Processing {text_type} files using {api_name} API")
    api_post = api_info["post_parameters"]
    api_response = api_info["response_parameters"]

    endpoint = api_post["endpoint"]
    headers = api_post["headers"]
    body = api_post["body"]

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), "r") as f:
                text = f.read()
                # TODO: figure out how to dynamically change the body if some APIs require different parameters
                body["content"] = text
                parameters = body.copy()
                print(body)
                response = requests.post(endpoint, headers=headers, json=parameters)
                if response.status_code != 200:
                    print(f"Error: {response.text}")
                    continue

                data = response.json()
                with open(output_csv, "a", newline="") as file:
                    writer = csv.writer(file)
                    # TODO: dynamically write the original and fake scores
                    writer.writerow(
                        [
                            filename,
                            text_type,
                            api_name,
                            data[api_response]["original"],
                            data[api_response]["fake"],
                        ]
                    )


# Different endpoints and their corresponding API keys, versions and request parameters
API_ENDPOINTS = {
    "Originality": {
        "post_parameters": {
            "endpoint": "https://api.originality.ai/api/v1/scan/ai",
            "body": {"content": "sample text", "aiModelVersion": "1"},
            "headers": {"X-OAI-API-KEY": "", "Accept": "application/json"},
            "API_KEY_POINTER": {
                "location": "headers",
                "value": "",
                "key_name": "X-OAI-API-KEY",
            },
        },
        "response_parameters": {
            "score": {
                "original": "",
                "fake": "",
            }
        },
    },
    "Sapling": {
        "post_parameters": {
            "endpoint": "https://api.sapling.ai/api/v1/aidetect",
            "parameters": {"text": "Sample"},
            "API_KEY_POINTER": {"location": "body", "value": "", "key_name": "key"},
        },
        "response_parameters": {"score": ""},
    },
    # Add more endpoints as needed
}


def api_constructor(selected_endpoints):
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
            api_info["post_parameters"]["parameters"][
                api_info["post_parameters"]["API_KEY_POINTER"]["key_name"]
            ] = api_key
        del api_info["post_parameters"]["API_KEY_POINTER"]
        # Add the modified API info to the api_settings dictionary
        api_settings[api_name] = api_info

    return api_settings


def main():
    print(
        "Welcome to the API Interaction Program. Please check the following API endpoints you wish to use: "
    )
    selected_endpoints = {}
    for api_name in API_ENDPOINTS:
        is_selected = input(f"Type Y/N to select {api_name} API: ")
        if is_selected.upper() == "Y":
            api_info = input("Please enter your API key: ")
            if api_info is None:
                print("Invalid API Key")
                break
            selected_endpoints[api_name] = api_info

    api_settings = api_constructor(selected_endpoints)

    ai_directory = input("Enter the directory path for AI text files: ")
    human_directory = input("Enter the directory path for human text files: ")

    for api_name, api in api_settings.items():
        process_files(ai_directory, "AI", api_name, api)
        process_files(human_directory, "Human", api_name, api)


if __name__ == "__main__":
    main()
