from chromadb import PersistentClient
from chromadb.errors import NotFoundError

from prompts.new_entity_dev_prompt import new_entity_dev_prompt

from states.cluster_dev_state import ClusterDevState
from config import chroma_db_client_path, collection_name, master_collection_name, SIMPLE_MODEL_NAME, COMPLEX_MODEL_NAME, OPENROUTER_EMBEDDING_MODEL_NAME
from src.utils import extract_json_from_llm, call_openrouter_embeddings, call_openrouter_llm

client = PersistentClient(path=chroma_db_client_path)
master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
sectional_collection = client.get_or_create_collection(name=collection_name)


def _get_master_collection():
    """Fetch a fresh handle to the master KG collection to avoid stale UUIDs after deletion."""
    return client.get_or_create_collection(name=master_collection_name)


def new_entity_dev_agent(state: ClusterDevState):
    master_collection = _get_master_collection()

    # Refresh handle if the collection was dropped and recreated elsewhere.
    try:
        existing_entity_list = master_collection.get().get("ids", [])
    except NotFoundError:
        master_collection = _get_master_collection()
        existing_entity_list = master_collection.get().get("ids", [])

    messages = new_entity_dev_prompt(
        state["section"]["proto_heading"],
        state["section"]["description"],
        state["section"]["proto_dm"],
        existing_entity_list,
    )
    response_json = extract_json_from_llm(call_openrouter_llm(messages, COMPLEX_MODEL_NAME))

    description_embedding = call_openrouter_embeddings(
        [response_json.get("description", "")],
        model_name=OPENROUTER_EMBEDDING_MODEL_NAME,
    )[0]

    master_kg_entity_update = {
        "heading": response_json.get("heading", ""),
        "description": response_json.get("description", ""),
        "embedding": description_embedding,
        "proto_dm": str(response_json.get("proto_dm")),
    }

    return {
        "master_kg_entity": master_kg_entity_update
    }