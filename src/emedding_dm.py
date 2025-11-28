import os
from pathlib import Path
from glob import glob
from dotenv import load_dotenv

from openai import OpenAI

from chromadb import PersistentClient

from prompts.proto_sectional_desc import prompt_for_proto_sectional_dm
from src.utils import extract_proto_messages, generate_random_id, call_openrouter_llm
from config import chroma_db_client_path, collection_name, OPENROUTER_EMBEDDING_MODEL_NAME, SIMPLE_MODEL_NAME


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
        print(f"Extracting page {os.path.basename(page_proto_dm_path)}")
        with open(page_proto_dm_path, "r") as f:
            page_proto_dm = f.read()
        
        
        proto_dict = extract_proto_messages(page_proto_dm)
        proto_list = [v for _, v in proto_dict.items()]
        sectional_desc_proto_list = []
        for proto_sectional_dm in proto_list:
            messages = prompt_for_proto_sectional_dm(proto_sectional_dm)
            try:
                llm_response = call_openrouter_llm(messages, SIMPLE_MODEL_NAME)
                sectional_desc_proto_list.append(llm_response)
            except:
                sectional_desc_proto_list.append("")

        embeddings = openai_client.embeddings.create(
            model=OPENROUTER_EMBEDDING_MODEL_NAME,
            input = sectional_desc_proto_list, 
            encoding_format="float"
        )

        embedding_list = [e.embedding for e in embeddings.data]
        metadata_list = [{"sectional_headings": key, "sectional_dm": value, "page_proto_dm_path": page_proto_dm_path} for key, value in proto_dict.items()]
        ids = [f"{generate_random_id()}_{key}" for key in proto_dict.keys()]

        collection.add(
            documents=sectional_desc_proto_list,        # list[str] - Make sure proto_list is defined
            embeddings=embedding_list,   # list[list[float]]
            ids=ids,                     # list[str]
            metadatas=metadata_list
        )




        




