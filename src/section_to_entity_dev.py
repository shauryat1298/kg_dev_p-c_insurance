import numpy as np
from langgraph.graph import StateGraph, END
import os
from chromadb import PersistentClient

from states.cluster_dev_state import ClusterDevState
from agents.section_entity_matching_agent import section_entity_matching_agent
from agents.new_entity_dev_agent import new_entity_dev_agent
from agents.entity_improving_bool_agent import entity_improving_bool_agent
from agents.entity_improving_agent import entity_improving_agent
from agents.load_master_db_agent import load_master_db_agent

from config import chroma_db_client_path, collection_name, master_collection_name

client = PersistentClient(path=chroma_db_client_path)
master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
sectional_collection = client.get_or_create_collection(name=collection_name)

def build_cluster_dev_graph_workflow():
    builder = StateGraph(ClusterDevState)

    builder.add_node("section_entity_matching", section_entity_matching_agent)
    builder.add_node("new_entity_dev", new_entity_dev_agent)
    builder.add_node("entity_improving_bool", entity_improving_bool_agent)
    builder.add_node("entity_improving", entity_improving_agent)
    builder.add_node("load_master_db", load_master_db_agent)

    def new_existing_entity_routing_fn(state: ClusterDevState):
        if state.get("section_entity_match_bool"):
            return "entity_improving_bool"
        else:
            return "new_entity_dev"

    def entity_improvement_required_routing_fn(state: ClusterDevState):
        if state.get("entity_improvement_required_bool"):
            return "entity_improving"
        else:
            return "end" 

    builder.add_conditional_edges(
        "section_entity_matching",
        new_existing_entity_routing_fn,
        {
            "new_entity_dev": "new_entity_dev",
            "entity_improving_bool": "entity_improving_bool"
        }
    )

    builder.add_conditional_edges(
        "entity_improving_bool",
        entity_improvement_required_routing_fn,
        {
            "entity_improving": "entity_improving",
            "end": END
        }
    )

    builder.add_edge("new_entity_dev", "load_master_db")
    builder.add_edge("entity_improving", "load_master_db")
    builder.add_edge("load_master_db", END)

    builder.set_entry_point("section_entity_matching")

    graph = builder.compile()

    return graph