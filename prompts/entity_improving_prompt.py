

def entity_improving_prompt(section_heading, section_description, section_proto_dm, entity_heading, entity_description, entity_proto_dm):
    
    system_prompt = f"""
    You are tasked with improving the existing entity for a knowledge graph based on a broker supplemental application form section for this Line of Business.

    Section Heading: {section_heading}
    Section Description: {section_description}
    Section Proto Data Model: {section_proto_dm}

    Entity Heading: {entity_heading}
    Entity Description: {entity_description}
    Entity Proto Data Model: {entity_proto_dm}

    Your goal:
    - Analyze the section heading, description, and proto data model.
    - Decide on how you can improve the existing entity data model
    - Return a JSON object ONLY, with an improved Entity Data model capturing more data points

    JSON format:
    {{
        "heading": "<new entity heading if required>",
        "description": "<brief description of the entity>",
        "proto_dm": "<new structured representation of the entity data model (if applicable)>"
    }}

    STRICTLY RETURN ONLY THE JSON OBJECT WITHOUT ANY EXPLANATIONS!
    """
    return [{"role": "system", "content": system_prompt}]

