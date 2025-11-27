import os
from pathlib import Path
from glob import glob
from dotenv import load_dotenv

from openai import OpenAI

from chromadb import PersistentClient

from src.utils import extract_proto_messages
from config import BASE_PATH, ARTIFACTS_PATH, chroma_db_client_path, collection_name


load_dotenv()

client = PersistentClient(path=chroma_db_client_path)
collection = client.get_or_create_collection(name=collection_name)

openai_client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)


def embed_data_models(form_proto_dm_dir_path):

    page_proto_dm_paths = glob(os.path.join(form_proto_dm_dir_path, "*.proto"), recursive=True)
    for page_proto_dm_path in page_proto_dm_paths:
        with open(page_proto_dm_path, "r") as f:
            page_proto_dm = f.read()
        
        proto_dict = extract_proto_messages(page_proto_dm)
        proto_list = [v for _, v in proto_dict.items()]
        embeddings = openai_client.embeddings.create(
            model="sentence-transformers/all-minilm-l12-v2",
            input = proto_list, 
            encoding_format="float"
        )

        embedding_list = [e.embedding for e in embeddings.data]
        


        




