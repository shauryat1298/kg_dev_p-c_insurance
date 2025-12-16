from typing import TypedDict, List

Vector = List[float]

class SectionState(TypedDict, total=False):
    description: str
    embedding: Vector
    proto_heading: str
    proto_dm: str
    page_proto_dm_path: str

class KGEntityState(TypedDict, total=False):
    heading: str
    description: str
    embedding: Vector
    proto_dm: str

class ClusterDevState(TypedDict, total=False):
    section: SectionState
    master_kg_entity: KGEntityState
    section_entity_match_bool: bool
    entity_improvement_required_bool: bool
    matched_entity_id: str