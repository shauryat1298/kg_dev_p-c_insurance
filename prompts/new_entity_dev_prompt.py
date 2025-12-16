

def new_entity_dev_prompt(proto_heading, description, proto_dm, existing_entity_list):
    system_prompt = f"""
    You are tasked with creating a new entity for a knowledge graph based on a broker supplemental application form section for this Line of Business.

    Existing entities: {existing_entity_list}

    Section Heading: {proto_heading}
    Section Description: {description}
    Section Proto Data Model: {proto_dm}

    Your goal:
    - Analyze the section heading, description, and proto data model.
    - Identify and define a new entity that is distinct from existing entities.
    - Return a JSON object ONLY, without any explanation or extra text.

    JSON format:
    {{
        "heading": "<concise entity heading>",
        "description": "<brief description of the entity>",
        "proto_dm": "<structured representation of the entity data model>"
    }}

    STRICTLY RETURN ONLY THE JSON OBJECT.
    """
    return [{"role": "system", "content": system_prompt}]

