import os
from pathlib import Path
from glob import glob

from dotenv import load_dotenv
import asyncio
import aiofiles

from prompts.form_page_dm import prompt_for_page_dm
from src.utils import extract_proto_code_for_llm_response, call_openrouter_llm, call_openrouter_llm_async

from config import BASE_PATH, ARTIFACTS_PATH, forms_proto_dm_dir_path, forms_png_dir_path, COMPLEX_MODEL_NAME, extra_body

from openai import OpenAI


load_dotenv()

async def convert_png_dir_to_proto_dm_async(form_png_dir_path, form_proto_dm_dir_path):
    form_pdf_name = os.path.basename(form_png_dir_path)
    os.makedirs(form_proto_dm_dir_path, exist_ok=True)

    form_png_paths = glob(os.path.join(form_png_dir_path, "*.png"), recursive=True)
    tasks = [process_single_png_async(form_png_path, form_proto_dm_dir_path) for form_png_path in form_png_paths]
    
    await asyncio.gather(*tasks)
    return form_pdf_name

async def process_single_png_async(form_png_path, form_proto_dm_dir_path):
    messages = prompt_for_page_dm(form_png_path)
    
    proto_dm_response = extract_proto_code_for_llm_response(await call_openrouter_llm_async(messages, COMPLEX_MODEL_NAME))

    png_name = os.path.basename(form_png_path)
    proto_dm_name = png_name[:-4] + ".proto"
    proto_dm_path = os.path.join(form_proto_dm_dir_path, proto_dm_name)
    
    async with aiofiles.open(proto_dm_path, "w") as f:
        await f.write(proto_dm_response)
        

