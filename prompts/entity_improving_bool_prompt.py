

def entity_improving_bool_prompt(section_heading, section_description, section_proto_dm, entity_heading, entity_description, entity_proto_dm):

    system_prompt = f"""
    You are being given a supplemental application form's sectional description and an independent entity information.
    Your job is to decide if the sectional description improves the data points captured in the entity.

    Sectional Information: {section_heading} - {section_description}
    Sectional Proto Data Model: {section_proto_dm}
    Entity Information: {entity_heading} - {entity_description}
    Entity Proto Data Model: {entity_proto_dm}

    RETURN TRUE OR FALSE WITHOUT ANY EXPLANATIONS!
    """

    return [{"role": "system", "content": system_prompt}]