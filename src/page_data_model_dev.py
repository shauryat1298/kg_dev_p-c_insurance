import os
from pathlib import Path
from glob import glob

from dotenv import load_dotenv

from prompts.form_page_dm import prompt_for_page_dm
from src.utils import extract_proto_code_for_llm_response

from config import BASE_PATH, ARTIFACTS_PATH, forms_proto_dm_dir_path, forms_png_dir_path, OPENROUTER_MODEL_NAME

from openai import OpenAI


load_dotenv()


def call_llm_to_get_page_dm(png_path):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    response = client.chat.completions.create(
        model = OPENROUTER_MODEL_NAME,
        messages = prompt_for_page_dm(png_path),
        extra_body={"reasoning": {"enabled": False}}
    )

    return response.choices[0].message.content

def convert_png_dir_to_proto_dm(form_png_dir_path, form_proto_dm_dir_path):

    form_png_paths = glob(os.path.join(form_png_dir_path, "*.png"), recursive=True)
    for form_png_path in form_png_paths:
        proto_dm_response = extract_proto_code_for_llm_response(call_llm_to_get_page_dm(form_png_path))

        png_name = os.path.basename(form_png_path)
        proto_dm_name = png_name[:-4]+".proto"
        proto_dm_path = os.path.join(form_proto_dm_dir_path, proto_dm_name)
        with open(proto_dm_path, "w") as f:
            f.write(proto_dm_response)
        

