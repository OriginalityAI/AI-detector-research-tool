import requests
import json
import os
import csv


output_csv = "output.csv"
global_organizationId = ""
copyLeaks_scan_id = 0


def process_files(directory, text_type, api_name, api_info):
    print(f"Processing {text_type} files using {api_name} API")
    api_post = api_info["post_parameters"]
    api_response = api_info["response"]["200"]
    text_key = api_post.get("text_key", "content")
    global global_organizationId
    global copyLeaks_scan_id

    endpoint = api_post["endpoint"]
    if "headers" in api_post:
        headers = api_post["headers"]
    else:
        headers = {}
    body = api_post["body"]

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), "r") as f:
                text = f.read()
                body[text_key] = text
                parameters = body.copy()
                copyLeaks_scan_id += 1
                response = requests.post(endpoint, headers=headers, json=parameters)
                if response.status_code != 200:
                    print(f"Error: {response.text}")
                    continue

                data = response.json()
                row = [text_type, api_name, filename]

                if isinstance(api_response, list):
                    for item in data:
                        for key, value in item.items():
                            if key in api_response:
                                row.append(value)
                else:
                    for key, value in api_response.items():
                        if isinstance(data[key], dict):
                            for sub_key, sub_value in data[key].items():
                                row.append(sub_value)
                        elif isinstance(data[key], list):
                            for sub_dict in data[key]:
                                for sub_key, sub_value in sub_dict.items():
                                    if sub_key in value:
                                        row.append(sub_value)
                        else:
                            row.append(data[key])

                print(f"Rows: {row}")
                with open(output_csv, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(row)

                print(f"File {filename} processed successfully")


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
            "text_key": "content",
        },
        "response": {
            "200": {
                "score": {
                    "ai": "",
                    "original": "",
                }
            }
        },
    },
    "Sapling": {
        "post_parameters": {
            "endpoint": "https://api.sapling.ai/api/v1/aidetect",
            "body": {"text": ""},
            "API_KEY_POINTER": {"location": "body", "value": "", "key_name": "key"},
            "text_key": "text",
        },
        "response": {"200": {"score": "score"}},
    },
    "Writer.com": {
        "post_parameters": {
            "endpoint": f"https://enterprise-api.writer.com/content/organization/{global_organizationId}/detect",
            "headers": {"Authorization": "", "Content-Type": "application/json"},
            "body": {"input": "Sample"},
            "API_KEY_POINTER": {
                "location": "headers",
                "value": "",
                "key_name": "Authorization",
            },
            "text_key": "input",
        },
        "response": {"200": ["score"]},
    },
    "GPTZero": {
        "post_parameters": {
            "endpoint": "https://api.gptzero.me/v2/predict/text",
            "body": {"document": "Sample", "version": "2023-05-23"},
            "headers": {"x-api-key": "", "Content-Type": "application/json"},
            "API_KEY_POINTER": {
                "location": "headers",
                "value": "",
                "key_name": "x-api-key",
            },
            "text_key": "document",
        },
        "response": {"200": {"documents": ["completely_generated_prob"]}},
    },
    "ZeroGPT": {
        "post_parameters": {
            "endpoint": "https://zerogpt.p.rapidapi.com/api/v1/detectText",
            "body": {"input_text": "Sample"},
            "headers": {"X-RapidAPI-Key": "", "Content-Type": "application/json"},
            "API_KEY_POINTER": {
                "location": "headers",
                "value": "",
                "key_name": "X-RapidAPI-Key",
            },
            "text_key": "input_text",
        },
        "response": {
            "200": {
                "is_human_written": "",
                "is_gpt_generated": "",
            }
        },
    },
    "Copyleaks": {
        "post_parameters": {
            "endpoint": f"https://api.copyleaks.com/v2/writer-detector/{copyLeaks_scan_id}/check",
            "headers": {},
            "body": {"text": "Sample"},
            "API_KEY_POINTER": {
                "location": "headers",
                "value": "",
                "key_name": "Authorization",
            },
            "text_key": "text",
        },
        "response": {"200": {"summary": [{"ai": "ai", "human": "human"}]}},
    }
    # Add more endpoints as needed
}


def get_nested_value(dictionary, keys):
    for key in keys:
        if isinstance(dictionary, list):
            dictionary = [
                sub_dict.get(key, None) if isinstance(sub_dict, dict) else None
                for sub_dict in dictionary
            ]
        else:
            dictionary = dictionary.get(key, None)
    return dictionary


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
            api_info["post_parameters"]["body"][
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
            if api_name == "Writer.com":
                global global_organizationId
                global_organizationId = input("Please enter your Organization ID: ")
                if global_organizationId is None:
                    print("Invalid Organization ID")
                    break
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
