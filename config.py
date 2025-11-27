import os
from pathlib import Path

BASE_PATH = Path("C:/Users/shaur/Desktop/Learnings/lob_kg_dev")
ARTIFACTS_PATH = os.path.join(BASE_PATH, "artifacts")

forms_pdf_dir_path = os.path.join(ARTIFACTS_PATH, "forms_pdf") 
forms_png_dir_path = os.path.join(ARTIFACTS_PATH, "forms_png") 
forms_proto_dm_dir_path = os.path.join(ARTIFACTS_PATH, "forms_proto_dm")

chroma_db_client_path = os.path.join(ARTIFACTS_PATH, "chroma_db_client")
collection_name = "construction_lob"

# Model Used in OpenRouter
OPENROUTER_MODEL_NAME = "anthropic/claude-sonnet-4.5"
OPENROTUER_EMBEDDING_MODEL_NAME = "sentence-transformers/all-minilm-l12-v2"
extra_body = {}
