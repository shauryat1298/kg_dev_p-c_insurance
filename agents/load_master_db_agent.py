from chromadb import PersistentClient

from states.cluster_dev_state import ClusterDevState
from config import chroma_db_client_path, collection_name, master_collection_name, SIMPLE_MODEL_NAME, COMPLEX_MODEL_NAME, OPENROUTER_EMBEDDING_MODEL_NAME
from src.utils import extract_json_from_llm, call_openrouter_embeddings, call_openrouter_llm

client = PersistentClient(path=chroma_db_client_path)
master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
sectional_collection = client.get_or_create_collection(name=collection_name)

def load_master_db_agent(state: ClusterDevState):

    try:
        if state['entity_improvement_required_bool']:
            master_kg_entity_collection.delete(ids=[state['matched_entity_id']])
    except:
        pass

    master_kg_entity_collection.add(
        ids = [state['master_kg_entity']['heading']],
        embeddings = [state['master_kg_entity']['embedding']],
        documents = [state['master_kg_entity']['description']],
        metadatas = [{"proto_dm": state['master_kg_entity']['proto_dm']}]
    )
