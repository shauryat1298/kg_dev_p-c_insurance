from chromadb import PersistentClient

from states.cluster_dev_state import ClusterDevState
from config import chroma_db_client_path, collection_name, master_collection_name, SIMPLE_MODEL_NAME, COMPLEX_MODEL_NAME, OPENROUTER_EMBEDDING_MODEL_NAME
from src.utils import extract_json_from_llm, call_openrouter_embeddings, call_openrouter_llm
from src.logging_config import get_logger

logger = get_logger(__name__)

client = PersistentClient(path=chroma_db_client_path)
master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
sectional_collection = client.get_or_create_collection(name=collection_name)

def load_master_db_agent(state: ClusterDevState):
    entity_heading = state.get("master_kg_entity", {}).get("heading", "unknown")
    improvement_required = state.get("entity_improvement_required_bool", False)
    matched_entity_id = state.get("matched_entity_id")
    
    logger.debug("load_master_db_started", entity_heading=entity_heading, improvement_required=improvement_required)

    try:
        if state['entity_improvement_required_bool']:
            logger.info("deleting_old_entity", entity_id=matched_entity_id)
            master_kg_entity_collection.delete(ids=[state['matched_entity_id']])
    except Exception as e:
        logger.warning("entity_deletion_error", entity_id=matched_entity_id, error=str(e), exc_info=True)

    try:
        master_kg_entity_collection.add(
            ids = [state['master_kg_entity']['heading']],
            embeddings = [state['master_kg_entity']['embedding']],
            documents = [state['master_kg_entity']['description']],
            metadatas = [{"proto_dm": state['master_kg_entity']['proto_dm']}]
        )
        logger.info("entity_added_to_master_db", entity_heading=entity_heading)
    except Exception as e:
        logger.error("entity_add_error", entity_heading=entity_heading, error=str(e), exc_info=True)
        raise
