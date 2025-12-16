from chromadb import PersistentClient

from prompts.entity_improving_prompt import entity_improving_prompt

from states.cluster_dev_state import ClusterDevState
from config import chroma_db_client_path, collection_name, master_collection_name, SIMPLE_MODEL_NAME, COMPLEX_MODEL_NAME, OPENROUTER_EMBEDDING_MODEL_NAME
from src.utils import extract_json_from_llm, call_openrouter_embeddings, call_openrouter_llm

client = PersistentClient(path=chroma_db_client_path)
master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
sectional_collection = client.get_or_create_collection(name=collection_name)

def entity_improving_agent(state: ClusterDevState):
    messages = entity_improving_prompt(
        state['section']['proto_heading'],
        state['section']['description'],
        state['section']['proto_dm'],
        state['master_kg_entity']['heading'],
        state['master_kg_entity']['description'],
        state['master_kg_entity']['proto_dm']
    )
    
    response_json = extract_json_from_llm(call_openrouter_llm(messages, COMPLEX_MODEL_NAME))
    description_embedding = call_openrouter_embeddings([response_json.get("description", "")], model_name=OPENROUTER_EMBEDDING_MODEL_NAME)[0]

    master_kg_entity_update = {
        "heading": response_json.get("heading", ""),
        "description": response_json.get("description", ""),
        "embedding": description_embedding,
        "proto_dm": str(response_json.get("proto_dm")),
    }

    return {
        "master_kg_entity": master_kg_entity_update
    }