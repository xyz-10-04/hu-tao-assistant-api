import os
from dotenv import load_dotenv
from openai import OpenAI
from config import MODEL_NAME, TEMPERATURE

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def call_api(messages):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=False,
        temperature=TEMPERATURE
    # reasoning_effort="high",
    # extra_body={"thinking": {"type": "enabled"}}
)
    return response