import os
from pathlib import Path

import re

from src.utils import encode_image

from config import BASE_PATH, ARTIFACTS_PATH, forms_proto_dm_dir_path


def prompt_for_page_dm(png_path):

    text_prompt = f"""
    You will be given an image of a PDF application form.

    1. First, determine whether the image contains any questions that require user responses. 
    - A question counts if it requests input (text fields, checkboxes, yes/no, blanks, multi-row tables, etc.).
    - If there are no questions, return an empty string ("") and stop.
    - If questions exist, continue.

    2. If questions are present, generate a complete Proto3-style data model that includes EVERY QUESTION in the form.
    - Include the question even if an answer is already filled in.
    - Organize the proto into multiple message objects based on semantic meaning.
    - Group related questions into the same message (e.g., ApplicantInformation, BusinessInformation, CoverageDetails, PropertyDetails, LossHistory, etc.).
    - Create additional message objects whenever needed to maintain logical grouping.
    - Use nested messages for subsections.
    - Use snake_case for field names.
    - For each field, add a brief comment summarizing the question.
    - Use appropriate Proto3 types (string, bool, int32, double, repeated).

    3. Output format:
    A. First line: "" (if no questions)
    B. If true, output the full Proto3 data model.


    """

    ## Check for existing previous png proto template
    proto_dir_path = os.path.join(forms_proto_dm_dir_path, os.path.basename(os.path.dirname(png_path)))
    png_name = os.path.basename(png_path)
    page_no= str(re.search(r'_(\d+)\.png$', png_name).group(1))

    if page_no!="001":
        prev_page_no = str(int(page_no)-1)
        if len(prev_page_no) == 1:
            prev_page_no = "00"+prev_page_no
        elif len(prev_page_no) == 2:
            prev_page_no = "0"+prev_page_no

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

    base64_img = encode_image(png_path)
    inf_img_media_type = "image/png"


    messages = [{"role": "user","content": 
                [
                    {
                    "type": "text",
                    "text": text_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_img}"
                        }
                    }
                ]
                }]
    
    return messages