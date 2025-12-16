import re
import os
import base64
import random
import string
import json

from openai import OpenAI

from config import extra_body, temperature

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
        temperature = temperature,
        extra_body=extra_body
    )

    return response.choices[0].message.content

def call_openrouter_embeddings(texts, model_name):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    response = client.embeddings.create(
        model=model_name,
        input=texts
    )
    # Returns list of embeddings (one per input text)
    return [e.embedding for e in response.data]


def generate_random_id(length: int = 8):
    return ''.join(random.choices(string.digits, k=length))

def extract_json_from_llm(string):
    string = string.replace("\n", "")
    json_start = -1
    brace_stack = []

    for i, char in enumerate(string):
        if char == "{":
            if json_start == -1:
                json_start = i
            brace_stack.append("{")
        elif char == "}":
            if brace_stack:
                brace_stack.pop()
            if not brace_stack:
                json_end = i+1
                json_str = string[json_start:json_end]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    return string
    return ""