import re
import base64

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def extract_proto_code_for_llm_response(text: str) -> str:
    # First, look for markdown code blocks with optional 'protobuf' hint
    match = re.search(r"```(?:protobuf)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # If no code block is found, but it starts with proto syntax, assume it's raw code
    if 'syntax = "proto3"' in text:
        # Heuristically extract from 'syntax' to end of message
        # This will assume the protobuf starts at the "syntax =" line
        start_idx = text.find('syntax = "proto3"')
        return text[start_idx:].strip().replace("```","")

    return ""