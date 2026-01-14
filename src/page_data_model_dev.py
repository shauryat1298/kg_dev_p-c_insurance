import os
from pathlib import Path
from glob import glob

from dotenv import load_dotenv
import asyncio
import aiofiles

from prompts.form_page_dm import prompt_for_page_dm
from src.utils import extract_proto_code_for_llm_response, call_openrouter_llm, call_openrouter_llm_async
from src.logging_config import get_logger

from config import BASE_PATH, ARTIFACTS_PATH, forms_proto_dm_dir_path, forms_png_dir_path, COMPLEX_MODEL_NAME, extra_body

from openai import OpenAI

logger = get_logger(__name__)

load_dotenv()

async def convert_png_dir_to_proto_dm_async(form_png_dir_path, form_proto_dm_dir_path):
    form_pdf_name = os.path.basename(form_png_dir_path)
    os.makedirs(form_proto_dm_dir_path, exist_ok=True)

    form_png_paths = sorted(glob(os.path.join(form_png_dir_path, "*.png"), recursive=True))
    logger.info("converting_png_to_proto_dm", form_name=form_pdf_name, png_count=len(form_png_paths))
    tasks = [process_single_png_async(form_png_path, form_proto_dm_dir_path) for form_png_path in form_png_paths]
    
    await asyncio.gather(*tasks)
    logger.info("png_to_proto_dm_completed", form_name=form_pdf_name)
    return form_pdf_name

async def process_single_png_async(form_png_path, form_proto_dm_dir_path):
    png_name = os.path.basename(form_png_path)
    logger.debug("processing_png", png_name=png_name)
    messages = prompt_for_page_dm(form_png_path)
    
    try:
        proto_dm_response = extract_proto_code_for_llm_response(await call_openrouter_llm_async(messages, COMPLEX_MODEL_NAME))
    except Exception as e:
        logger.error("png_processing_error", png_name=png_name, error=str(e), exc_info=True)
        return

    proto_dm_name = png_name[:-4] + ".proto"
    proto_dm_path = os.path.join(form_proto_dm_dir_path, proto_dm_name)
    
    try:
        async with aiofiles.open(proto_dm_path, "w") as f:
            await f.write(proto_dm_response)
        logger.debug("proto_dm_saved", png_name=png_name, proto_path=proto_dm_path)
    except Exception as e:
        logger.error("proto_dm_save_error", png_name=png_name, proto_path=proto_dm_path, error=str(e), exc_info=True)
        

