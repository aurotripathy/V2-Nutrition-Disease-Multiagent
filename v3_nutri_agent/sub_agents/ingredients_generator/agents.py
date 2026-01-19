

ingredients_generator_agent = LlmAgent(
    name="IngredientsGenerator",
    model=model,
    instruction=INGREDIENTS_GENERATOR_INSTRUCTIONS,
    description=INGREDIENTS_GENERATOR_DESCRIPTION,
    # tools=[get_nutriments_from_off, google_search],
    tools=[get_grouped_nutriments_from_open_food_facts],
    output_schema=IngredientsListAndAilment,
    output_key="ingredients_list_and_ailment",  # Save result to state
)