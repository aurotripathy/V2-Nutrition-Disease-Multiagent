

disease_identifier_agent = LlmAgent(
    name="DiseaseIdentifier",
    model=model,
    instruction=load_instruction_from_file("disease_identifier_instructions.txt"),
    tools=[google_search],
)