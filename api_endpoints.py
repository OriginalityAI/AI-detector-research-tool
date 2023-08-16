from dotenv import load_dotenv
import os

load_dotenv()

# API keys
ORIGINALITY_API_KEY = os.getenv("ORIGINALITY_API_KEY")
SAPLING_API_KEY = os.getenv("SAPLING_API_KEY")
WRITER_API_KEY = os.getenv("WRITER_API_KEY")
GPTZERO_API_KEY = os.getenv("GPTZERO_API_KEY")
COPYLEAKS_API_KEY = os.getenv("COPYLEAKS_API_KEY")


# Different endpoints and their corresponding API keys, versions and request parameters
API_ENDPOINTS = {
    "Originality": {
        "post_parameters": {
            "endpoint": "https://api.originality.ai/api/v1/scan/ai",
            "body": {"content": "sample text", "aiModelVersion": "1"},
            "headers": {"X-OAI-API-KEY": "", "Accept": "application/json"},
            "API_KEY_POINTER": {
                "location": "headers",
                "value": ORIGINALITY_API_KEY,
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
            "body": {"text": "", "key": ""},
            "API_KEY_POINTER": {"location": "body", "value": SAPLING_API_KEY, "key_name": "key"},
            "text_key": "text",
        },
        "response": {"200": {"score": "score"}},
    },
    "Writer": {
        "post_parameters": {
            "endpoint": "https://enterprise-api.writer.com/content/organization/{writer_organization_id}/detect",
            "headers": {"Authorization": "", "Content-Type": "application/json"},
            "body": {"input": "Sample"},
            "API_KEY_POINTER": {
                "location": "headers",
                "value": WRITER_API_KEY,
                "key_name": "Authorization",
            },
            "text_key": "input",
        },
        "response": {"200": ["score"]},
    },
    "GPTZero": {
        "post_parameters": {
            "endpoint": "https://api.gptzero.me/v2/predict/text",
            "body": {"document": "Sample"},
            "headers": {"x-api-key": "", "Content-Type": "application/json"},
            "API_KEY_POINTER": {
                "location": "headers",
                "value": GPTZERO_API_KEY,
                "key_name": "x-api-key",
            },
            "text_key": "document",
        },
        "response": {"200": {"documents": ["completely_generated_prob"]}},
    },
    # "ZeroGPT": {
    #     "post_parameters": {
    #         "endpoint": "https://zerogpt.p.rapidapi.com/api/v1/detectText",
    #         "body": {"input_text": "Sample"},
    #         "headers": {"X-RapidAPI-Key": "", "Content-Type": "application/json"},
    #         "API_KEY_POINTER": {
    #             "location": "headers",
    #             "value": "",
    #             "key_name": "X-RapidAPI-Key",
    #         },
    #         "text_key": "input_text",
    #     },
    #     "response": {
    #         "200": {
    #             "is_human_written": "",
    #             "is_gpt_generated": "",
    #         }
    #     },
    # },
    "Copyleaks": {
        "post_parameters": {
            "endpoint": "https://api.copyleaks.com/v2/writer-detector/{copyLeaks_scan_id}/check",
            "headers": {},
            "body": {"text": "Sample"},
            "API_KEY_POINTER": {
                "location": "headers",
                "value": "Bearer " + COPYLEAKS_API_KEY,
                "key_name": "Authorization",
            },
            "text_key": "text",
        },
        "response": {"200": {"summary": {"ai": "ai"}}},
    }
    # Add more endpoints as needed
}
