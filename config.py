import os
from pathlib import Path

# Get project root directory (parent of config.py's parent directory)
# Support BASE_PATH override via environment variable for flexibility
BASE_PATH = Path(os.getenv("BASE_PATH", Path(__file__).parent))
ARTIFACTS_PATH = os.path.join(BASE_PATH, "artifacts")

forms_pdf_dir_path = os.path.join(ARTIFACTS_PATH, "forms_pdf") 
forms_png_dir_path = os.path.join(ARTIFACTS_PATH, "forms_png") 
forms_proto_dm_dir_path = os.path.join(ARTIFACTS_PATH, "forms_proto_dm")

chroma_db_client_path = os.path.join(ARTIFACTS_PATH, "chroma_db_client")
collection_name = "construction_lob"
master_collection_name = "kg_entity_construction"

# Model Used in OpenRouter
COMPLEX_MODEL_NAME = "anthropic/claude-sonnet-4.5"
SIMPLE_MODEL_NAME = "openai/gpt-5-nano"
OPENROUTER_EMBEDDING_MODEL_NAME = "sentence-transformers/all-minilm-l12-v2"
extra_body = {}
temperature = 0
