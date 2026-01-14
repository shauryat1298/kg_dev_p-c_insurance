import re
import os
import base64
import random
import string
import json

import asyncio
from openai import OpenAI, AsyncOpenAI, APIError, RateLimitError
from dotenv import load_dotenv
from config import extra_body, temperature
from src.logging_config import get_logger

logger = get_logger(__name__)

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
    logger.debug("llm_api_call", model=model_name)
    try:
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
        logger.debug("llm_api_success", model=model_name)
        return response.choices[0].message.content
    except Exception as e:
        logger.error("llm_api_error", model=model_name, error=str(e), exc_info=True)
        raise

load_dotenv()
async_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

async def call_openrouter_llm_async(messages, model_name, max_retries=3):
    for attempt in range(max_retries):
        try:
            logger.debug("llm_api_call", model=model_name, attempt=attempt + 1)
            response = await async_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                extra_body=extra_body
            )
            logger.debug("llm_api_success", model=model_name, attempt=attempt + 1)
            return response.choices[0].message.content
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt 
                logger.warning("rate_limit_retry", model=model_name, attempt=attempt + 1, wait_time=wait_time)
                await asyncio.sleep(wait_time)
            else:
                logger.error("rate_limit_exceeded", model=model_name, max_retries=max_retries)
                raise
        except APIError as e:
            logger.error("llm_api_error", model=model_name, attempt=attempt + 1, error=str(e), exc_info=True)
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)

def call_openrouter_embeddings(texts, model_name):
    logger.debug("embeddings_api_call", model=model_name, text_count=len(texts))
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        response = client.embeddings.create(
            model=model_name,
            input=texts
        )
        # Returns list of embeddings (one per input text)
        logger.debug("embeddings_api_success", model=model_name, count=len(response.data))
        return [e.embedding for e in response.data]
    except Exception as e:
        logger.error("embeddings_api_error", model=model_name, error=str(e), exc_info=True)
        raise

async def call_openrouter_embeddings_async(texts, model_name, max_retries=3):
    for attempt in range(max_retries):
        try:
            logger.debug("embeddings_api_call", model=model_name, text_count=len(texts), attempt=attempt + 1)
            response = await async_client.embeddings.create(
                model=model_name,
                input=texts
            )
            # Returns list of embeddings (one per input text)
            logger.debug("embeddings_api_success", model=model_name, count=len(response.data), attempt=attempt + 1)
            return [e.embedding for e in response.data]
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning("rate_limit_retry", model=model_name, attempt=attempt + 1, wait_time=wait_time)
                await asyncio.sleep(wait_time)
            else:
                logger.error("rate_limit_exceeded", model=model_name, max_retries=max_retries)
                raise
        except APIError as e:
            logger.error("embeddings_api_error", model=model_name, attempt=attempt + 1, error=str(e), exc_info=True)
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)


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