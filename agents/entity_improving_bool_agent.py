from chromadb import PersistentClient

from prompts.entity_improving_bool_prompt import entity_improving_bool_prompt

from states.cluster_dev_state import ClusterDevState
from config import chroma_db_client_path, collection_name, master_collection_name, SIMPLE_MODEL_NAME, COMPLEX_MODEL_NAME, OPENROUTER_EMBEDDING_MODEL_NAME
from src.utils import extract_json_from_llm, call_openrouter_embeddings, call_openrouter_llm

client = PersistentClient(path=chroma_db_client_path)
master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
sectional_collection = client.get_or_create_collection(name=collection_name)

def entity_improving_bool_agent(state: ClusterDevState):
    messages = entity_improving_bool_prompt(
        state['section']['proto_heading'],
        state['section']['description'],
        state['section']['proto_dm'],
        state['master_kg_entity']['heading'],
        state['master_kg_entity']['description'],
        state['master_kg_entity']['proto_dm']
    )
    llm_response = call_openrouter_llm(messages, SIMPLE_MODEL_NAME).strip().lower()
    improvement_reqd_bool = "true" in llm_response
    
    return {
        "entity_improvement_required_bool": improvement_reqd_bool
    }