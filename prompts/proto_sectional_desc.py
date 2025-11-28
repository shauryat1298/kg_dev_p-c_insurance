import os
from pathlib import Path

import re
import json

from config import BASE_PATH, ARTIFACTS_PATH, forms_proto_dm_dir_path

def prompt_for_proto_sectional_dm(proto_dm_section):
    system_prompt = (
        "Given a proto3 data model of a supplemental application form, "
        "return a RAG-friendly continuous description that summarizes the data model. "
        "Please mind that description has to be embedded. Do not include explanations."
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": proto_dm_section},
    ]

