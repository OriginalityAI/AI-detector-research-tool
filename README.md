# AI detector research tool

## Overview

This tool allows you to test the accuracy of various AI detectors. It is a command line tool designed to make it easy to test a large number of detectors at the same time using the same data.

## Description

The tool takes a set of text files and runs them through a number of AI detectors. It then outputs the results to a CSV file. The tool also generates a confusion matrix to show the accuracy of the detectors. But what is a confusion matrix? A confusion matrix is a table that is used to describe the performance of a classification model. It shows the number of correct and incorrect predictions made by the classification model compared to the actual outcomes. This table is extremely useful for comparing the performance of different detectors as it will show the true positives, false positives, true negatives and false negatives for each detector. This allows you to see which detectors are the most accurate.

## Requirements

- Python 3.9 or higher
- API keys for the detectors you want to test

## Installation

1. Clone this repository
2. Install the requirements using `pip install -r requirements.txt`

## Usage

1. Make a note of your API keys for the detectors you want to test
2. Run the tool using `python main.py`
3. Follow the instructions in the tool adding your API keys when prompted
4. The tool will run the detectors and output the results to a CSV file

Sample workflow:

```bash
python main.py
Type Y/N to select Originality.ai API: y
Enter your Originality.ai API key: YOUR_API_KEY
Enter the directory path for AI text files: data/ai
Enter the directory path for human text files: data/human
Enter the output CSV file name: output.csv

Tool will process the data. This may take a while.
Would you like to generate a confusion matrix? (y/n): y
Press enter to exit...
```

## Usage notes

- The tool will only run the detectors you have API keys for
- If when the tool is finished you are not prompted to generate a confusion matrix or the generation fails run `python matrix.py` to generate the confusion matrix

## Input Data Format

The tool expects data to be in .txt files in a folder which is passed to the tool when it is run.

## Adding detectors

To add a detector you need to do the following:

1. Find the detectors API documentation
2. Find the endpoint for the detector
3. Find the parameters required for the endpoint
4. Add the detector to the `detectors.py` file in the following format:

```"YOUR_DETECTOR_NAME": {
    "post_parameters": {
        # The endpoint URL for the API.
        "endpoint": "YOUR_API_ENDPOINT_URL",

        # The body of the POST request. This usually contains the text to be analyzed.
        # The actual contents will depend on what the API expects.
        # Add or remove parameters as needed depending on the API requirements.
        "body": {"PARAMETER_NAME": "PARAMETER_VALUE"},

        # The headers for the POST request. This usually includes the API key and content type.
        # Add or remove headers as needed depending on the API requirements.
        "headers": {"HEADER_NAME": "HEADER_VALUE"},

        # Information about where the API key is included in the request.
        "API_KEY_POINTER": {
            # The location that the API key will end up (usually 'headers' or 'body').
            "location": "headers_or_body",

            # The actual API key. This is usually read from an environment variable or input by the user.
            "value": "YOUR_API_KEY",

            # The name of the key or field where the API key is included. e.g 'x-api-key' or 'api_key'.
            "key_name": "API_KEY_HEADER_OR_PARAMETER_NAME",
        },

        # The key in the body of the POST request where the text to be analyzed is included. e.g 'text' or 'content'.
        "text_key": "KEY_NAME_FOR_TEXT",
    },

    "response": {
        # The expected response from the API. The actual structure will depend on what the API returns.
        # This should include mappings for how to interpret the API's response.
        # Add or remove mappings as needed.
        # e.g if the API returns a JSON object with a key called 'result' and the value of 'result' is a list of objects
        # with a key called 'score' then the mapping would be:
        # "result": {
        #     "score": "result.score"
        # }
        "200": {
            "result": {
                "MAPPING_FOR_DESIRED_OUTPUT": "RESPONSE_KEY_PATH",
            }
        }
    },
}
```

## Links to api docs for some detectors

- Originality.ai [API](https://docs.originality.ai/)
- Sapling.ai [API](https://sapling.ai/docs/api/detector)
- GPTZero [API](https://gptzero.stoplight.io/docs/gptzero-api/d2144a785776b-ai-detection-on-single-string)
- Writer.com [API](https://dev.writer.com/reference/contentdetectorapi)
- Copyleaks [API](https://api.copyleaks.com/documentation/v3/writer-detector)

## License

MIT License

Copyright (c) [2023] [Originality.AI]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
