from google.adk.agents.callback_context import CallbackContext
import json

DISEASE_ANALYSER_INSTRUCTIONS_TEMPLATE = """
**Your Core Identity and Sole Purpose:**
    You are an expert on diseases that can spring from consuming certain food ingredients.

**Strict Refusal Mandate:**
    Do no meander off-topic.
    If you are passed data other than an ingredients list and optionally, a disease or ailment to research, treat it as off-topic.
    For off-topic requests, respond with the exact phrase: "Sorry, I can only respond to food ingredients and optionally, a disease or ailment. I haven't been provided with the data to respond to your query."

**Required Sequence and Workflow:**
    You have been provided with the ingredients list and, optionally, a disease or ailment information from the parent agent (ingredients_generator).

    {INGREDIENTS_DATA}

    If the disease or ailment field is populated (not empty or None), stick to your research on that disease or ailment.
    You MUST use the AgentTool, 'search_for_diseases_agent' to find the diseases or health issues stemming from consuming the ingredients in the list provided.
    **CRITICAL: When calling 'search_for_diseases_agent', you MUST include ALL ingredients from the ingredients list in your request. Do NOT omit any ingredients.**

**Output**
     The output is a dictionary of the diseases or health issues stemming from consuming the ingredients in the ingredients data provided.
     Format: {"diseases": {...disease_data...}}
"""

def setup_disease_analyser_agent_instruction(callback_context: CallbackContext) -> str:
    """
    Dynamic instruction function that injects ingredients_list_and_ailment from state.
    """
    
    # Get the ingredients list from session state
    ingredients_data = callback_context.session.state.get('ingredients_list_and_ailment')
   
    if ingredients_data:
       
        # Format the ingredients data for the instruction
        if isinstance(ingredients_data, dict):
            ingredients_text = "**Ingredients List and Ailment Data:**\n"
            ingredients_text += f"```json\n{json.dumps(ingredients_data, indent=2)}\n```"
        else:
            print(f"[PROMPT] Disease Analyser: Ingredients List and Ailment data from the parent agent is not a dictionary. It is a string:\n{ingredients_data}")
            ingredients_text = f"**Ingredients List and Ailment Data:**\n{ingredients_data}"
    else:
        ingredients_text = "⚠️ No ingredients list found in state. The parent agent may not have provided the data yet."
    
    # Inject the ingredients data into the template
    print(f"[✨PROMPT] Disease Analyser: Ingredients dictionary assimilated from the parent agent into the prompt:\n```json\n{json.dumps(ingredients_data)}\n```")
    instruction = DISEASE_ANALYSER_INSTRUCTIONS_TEMPLATE.replace("{INGREDIENTS_DATA}", ingredients_text)
    
    return instruction

# Keep the old constant for backward compatibility, but it won't be used
DISEASE_ANALYSER_INSTRUCTIONS = DISEASE_ANALYSER_INSTRUCTIONS_TEMPLATE

DISEASE_ANALYSER_DESCRIPTION = """
Searches for diseases or health issues stemming from consuming the ingredients in the list provided.
"""

DISEASE_ANALYSER_SEARCH_AGENT_INSTRUCTIONS_TEMPLATE = """
**Your Core Identity and Sole Purpose:**
   You are a specialized disease search assistant.
   Your sole and exclusive purpose is to search for the diseases or health issues stemming from consuming the ingredients in the list provided.

{INGREDIENTS_DATA}

   You must use the 'google_search' tool to search for the diseases or health issues. 
   For your search query, you *MUST* use *ALL* the ingredients from the ingredients list provided above. 
   If you do NOT have this list, do NOT proceed with the search.
   Just output: "I don't have a list of ingredients to search for."
   Strictly maintain a JSON format as the output. Do not include any other text in the output. Do not include any other text in the output.
   The output is a dictionary of the diseases or health issues stemming from consuming the ingredients in the list provided.
"""

def setup_search_for_diseases_agent_instruction(callback_context: CallbackContext) -> str:
    """
    Dynamic instruction function that injects ingredients_list_and_ailment from state for the search agent.
    """
    
    # Get the ingredients list from session state
    ingredients_data = callback_context.session.state.get('ingredients_list_and_ailment')
    # print(f"[✨PROMPT] In state of get_disease_analyser_search_agent_instruction: {ingredients_data}")
    # print(f"[✨PROMPT] [STATE DEBUG] Session state keys check: 'ingredients_list_and_ailment' in state = {'ingredients_list_and_ailment' in callback_context.session.state}")
    # print(f"[✨PROMPT] [STATE DEBUG] Session state object ID: {id(callback_context.session.state)}")
    # print(f"[✨PROMPT] [STATE DEBUG] Session state type: {type(callback_context.session.state)}")
    
    # Try to get from invocation context if available
    if hasattr(callback_context, 'invocation_context'):
        inv_state = callback_context.invocation_context.session.state if hasattr(callback_context.invocation_context, 'session') else None
        if inv_state:
            inv_data = inv_state.get('ingredients_list_and_ailment')
            print(f"[✨PROMPT] [STATE DEBUG] Invocation context state has data: {inv_data is not None}")
            if inv_data and not ingredients_data:
                ingredients_data = inv_data
                print(f"[✨PROMPT] [STATE DEBUG] Using data from invocation context state")
    # print(f"[✨PROMPT] Disease Analyser Search Agent: Ingredients list and ailment data from the parent agent:\n```json\n{json.dumps(ingredients_data, indent=2)}\n```")
    
    if ingredients_data:
        # Inject ALL ingredients if it's a dict
        if isinstance(ingredients_data, dict):
            # Get all keys (ingredients)
            all_ingredients = list(ingredients_data.keys())
            ingredients_text = f"**All Ingredients to Search ({len(all_ingredients)} total):**\n"
            for i, ingredient in enumerate(all_ingredients, 1):
                ingredients_text += f"{i}. {ingredient}\n"
            ingredients_text += f"\n**Full Ingredients Data:**\n```json\n{json.dumps(ingredients_data, indent=2)}\n```"
        else:
            ingredients_text = f"**Ingredients List and Ailment Data:**\n{ingredients_data}"
    else:
        ingredients_text = "**WARNING:** No ingredients list found in state. The parent agent may not have provided the data yet."
    
    # Inject the ingredients data into the template
    print(f"[✨PROMPT] Disease Analyser Search Agent: Ingredients list and ailment data injected into the prompt:\n```json\n{json.dumps(ingredients_data)}\n```")
    instruction = DISEASE_ANALYSER_SEARCH_AGENT_INSTRUCTIONS_TEMPLATE.replace("{INGREDIENTS_DATA}", ingredients_text)
    
    return instruction

# Keep the old constant for backward compatibility
DISEASE_ANALYSER_SEARCH_AGENT_INSTRUCTIONS = DISEASE_ANALYSER_SEARCH_AGENT_INSTRUCTIONS_TEMPLATE

DISEASE_ANALYSER_SEARCH_AGENT_DESCRIPTION = """
Searches for the diseases or health issues stemming from consuming the ingredients in the list provided.
"""