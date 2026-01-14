from chromadb import PersistentClient
from chromadb.errors import NotFoundError
import numpy as np
from prompts.section_entity_matching_prompt import section_entity_matching_prompt

from states.cluster_dev_state import ClusterDevState
from config import chroma_db_client_path, collection_name, master_collection_name, SIMPLE_MODEL_NAME, COMPLEX_MODEL_NAME, OPENROUTER_EMBEDDING_MODEL_NAME
from src.utils import extract_json_from_llm, call_openrouter_embeddings, call_openrouter_llm
from src.logging_config import get_logger

logger = get_logger(__name__)

client = PersistentClient(path=chroma_db_client_path)
master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
sectional_collection = client.get_or_create_collection(name=collection_name)


def section_entity_matching_agent(state: ClusterDevState):
    section_heading = state.get("section", {}).get("proto_heading", "unknown")
    logger.debug("section_entity_matching_started", section_heading=section_heading)
    
    section_emb = state.get("section", {}).get("embedding")
    if section_emb is None or (isinstance(section_emb, (list, np.ndarray)) and len(section_emb) == 0):
        logger.warning("section_entity_matching_no_embedding", section_heading=section_heading)
        return {"section_entity_match_bool": False}

    # --- 1. Query top-1 entity safely ---
    top_matched_entity_result = master_kg_entity_collection.query(
        query_embeddings=[section_emb],
        n_results=1,
        include=["documents", "metadatas", "embeddings", "distances"]
    )

    if not top_matched_entity_result.get("ids") or not top_matched_entity_result["ids"][0]:
        logger.info("section_entity_matching_no_results", section_heading=section_heading)
        return {"section_entity_match_bool": False}

    # --- 2. Extract top match ---
    entity_heading = top_matched_entity_result["ids"][0][0]
    entity_description = top_matched_entity_result["documents"][0][0]
    entity_embedding = top_matched_entity_result["embeddings"][0][0]
    entity_proto_dm = top_matched_entity_result["metadatas"][0][0].get("proto_dm")
    distance = top_matched_entity_result.get("distances", [[None]])[0][0]

    logger.debug("section_entity_matching_candidate_found", 
                section_heading=section_heading, 
                entity_heading=entity_heading,
                distance=distance)

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

    logger.info("section_entity_matching_completed",
               section_heading=section_heading,
               entity_heading=entity_heading,
               is_match=is_match)

    # --- 5. Return updated state ---
    return {
        "master_kg_entity": master_kg_entity_update,
        "section_entity_match_bool": is_match,
        "matched_entity_id": entity_heading
    }
