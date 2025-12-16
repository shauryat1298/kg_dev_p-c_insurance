from chromadb import PersistentClient
import numpy as np
from prompts.section_entity_matching_prompt import section_entity_matching_prompt

from states.cluster_dev_state import ClusterDevState
from config import chroma_db_client_path, collection_name, master_collection_name, SIMPLE_MODEL_NAME, COMPLEX_MODEL_NAME, OPENROUTER_EMBEDDING_MODEL_NAME
from src.utils import extract_json_from_llm, call_openrouter_embeddings, call_openrouter_llm

client = PersistentClient(path=chroma_db_client_path)
master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
sectional_collection = client.get_or_create_collection(name=collection_name)

def section_entity_matching_agent(state: ClusterDevState):
    section_emb = state.get("section", {}).get("embedding")
    if section_emb is None or (isinstance(section_emb, (list, np.ndarray)) and len(section_emb) == 0):
        return {"section_entity_match_bool": False}

    # --- 1. Query top-1 entity safely ---
    top_matched_entity_result = master_kg_entity_collection.query(
        query_embeddings=[section_emb],
        n_results=1,
        include=["documents", "metadatas", "embeddings", "distances"]
    )

    if not top_matched_entity_result["ids"][0]:
        return {"section_entity_match_bool": False}

    # --- 2. Extract top match ---
    entity_heading = top_matched_entity_result["ids"][0][0]
    entity_description = top_matched_entity_result["documents"][0][0]
    entity_embedding = top_matched_entity_result["embeddings"][0][0]
    entity_proto_dm = top_matched_entity_result["metadatas"][0][0].get("proto_dm")

    # --- 3. Update master_kg_entity partial state ---
    master_kg_entity_update = {
        "heading": entity_heading,
        "description": entity_description,
        "embedding": entity_embedding,
        "proto_dm": entity_proto_dm,
    }

    # --- 4. Ask LLM for semantic match ---
    messages = section_entity_matching_prompt(
        state["section"].get("proto_heading", ""),
        state["section"].get("description", ""),
        entity_heading,
        entity_description,
    )

    llm_response = call_openrouter_llm(messages, SIMPLE_MODEL_NAME).strip().lower()
    is_match = "true" in llm_response

    # --- 5. Return updated state ---
    return {
        "master_kg_entity": master_kg_entity_update,
        "section_entity_match_bool": is_match,
        "matched_entity_id": entity_heading
    }
