import sys
import os
# Add project root to path for config import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from config import MODEL_GEMINI_2_5_FLASH

model = MODEL_GEMINI_2_5_FLASH

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