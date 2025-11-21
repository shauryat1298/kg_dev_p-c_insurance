import os
from pathlib import Path

BASE_PATH = Path("C:/Users/shaur/Desktop/Learnings/lob_kg_dev")
ARTIFACTS_PATH = os.path.join(BASE_PATH, "artifacts")

forms_pdf_dir_path = os.path.join(ARTIFACTS_PATH, "forms_pdf") 
forms_png_dir_path = os.path.join(ARTIFACTS_PATH, "forms_png") 
forms_proto_dm_dir_path = os.path.join(ARTIFACTS_PATH, "forms_proto_dm")

# Model Used
OPENROUTER_MODEL_NAME = "x-ai/grok-4.1-fast:free"
