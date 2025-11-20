import os
from pathlib import Path

import re

from src.utils import encode_image

from config import BASE_PATH, ARTIFACTS_PATH, forms_proto_dm_dir_path


def prompt_for_page_dm(png_path):

    text_prompt = f"""
    You will be provided the image of pdf application form.
    Does this image has any questions to be answered by user. Think of it as a True or False.
    If False, stop here and return an empty string.
    If True, Develop a proto data model (include all questions, ignore if they are answered or not). For every row, very briefly mention the question as a comment.
    """

    ## Check for existing previous png proto template
    proto_dir_path = os.path.join(forms_proto_dm_dir_path, "forms_proto_dm", os.path.basename(os.path.dirname(png_path)))
    png_name = os.path.basename(png_path)
    page_no= int(re.search(r'_(\d+)\.png$', png_name).group(1))

    if page_no!=1:
        prev_page_no = str(page_no-1)
        possible_previous_proto_name = re.sub(r'(\d+)(?=\.png$)', prev_page_no, png_name)[:-4]+".proto"
        possible_previous_proto_path = os.path.join(proto_dir_path, possible_previous_proto_name)

        if os.path.exists(possible_previous_proto_path):
            with open(possible_previous_proto_path, "r") as f:
                prev_proto_file = f.read()
        
            additional_info_in_prompt = f"""
            You are provided with the previous page data model to retain context. If you find any section as continuation of previous section, you can mention a small section contd. comment.
            previous image data model - {prev_proto_file}

            """
            text_prompt += additional_info_in_prompt


    text_prompt += "\n\nOnly return a proto3 syntax file. DON'T RETURN ANY EXPLANATIONS."

    inference_message = encode_image(png_path)
    inf_img_media_type = "image/png"


    messages = [{"role": "user","content": 
                [
                    {
                    "type": "image_base64",
                    "image_base64": {
                        "base64": f"data:image/png;base64,{inference_message}"
                    }
                    },
                    {
                    "type": "text",
                    "text": text_prompt
                    }
                ]
                }]
    
    return messages