import re
import os
import base64
import random
import string

from openai import OpenAI

from config import extra_body

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def extract_proto_code_for_llm_response(text: str) -> str:
    # First, look for markdown code blocks with optional 'protobuf' hint
    match = re.search(r"```(?:protobuf)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    if 'syntax = "proto3"' in text:
        start_idx = text.find('syntax = "proto3"')
        return text[start_idx:].strip().replace("```","")

    return ""

def extract_proto_messages(proto_content):
    messages = {}
    pattern = r'message\s+(\w+)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
    matches = re.finditer(pattern, proto_content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        message_name = match.group(1)
        message_body = match.group(2)
        messages[message_name] = f"message {message_name} {{{message_body}}}"
    
    return messages

def call_openrouter_llm(messages, model_name):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    response = client.chat.completions.create(
        model = model_name,
        messages = messages,
        extra_body=extra_body
    )

    return response.choices[0].message.content

def generate_random_id(length: int = 8):
    return ''.join(random.choices(string.digits, k=length))