

def section_entity_matching_prompt(section_heading, section_description, entity_heading, entity_description):

    system_prompt = f"""
    You are being given a supplemental application form's sectional description and an independent entity information.
    Your job is to decide if the sectional description has an overlap with the entity, the concept is partially/fully presented in the entity?

    Sectional Information: {section_heading} - {section_description}
    Entity Information: {entity_heading} - {entity_description}

    RETURN TRUE OR FALSE WITHOUT ANY EXPLANATIONS!
    """

    return [{"role": "system", "content": system_prompt}]