import os

from dotenv import load_dotenv

load_dotenv()
llm_config = {
    "config_list":[
        {
            "model":"gpt-4o",
            "api_type":"azure",
            "api_key":os.getenv("AZURE_OPENAI_API_KEY"),
            "base_url":os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_version":"2024-06-01",
        }
    ]
}
