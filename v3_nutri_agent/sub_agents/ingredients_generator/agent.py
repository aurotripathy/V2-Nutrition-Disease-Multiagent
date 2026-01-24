from google.adk.agents import Agent
from .schema_and_tools import get_grouped_nutriments_from_open_food_facts
from .prompts import INGREDIENTS_GENERATOR_INSTRUCTIONS, INGREDIENTS_GENERATOR_DESCRIPTION
import sys
import os
# Add project root to path for config import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from config import MODEL_GEMINI_2_5_FLASH

model = MODEL_GEMINI_2_5_FLASH



from google.adk.agents.callback_context import CallbackContext
from google.genai.types import Content
from typing import Optional

def before_ingredients_generator_callback(callback_context: CallbackContext) -> Optional[Content]:
    print(f"▶ Entering Agent: {callback_context.agent_name}")
    print(f" Invocation ID: {callback_context.invocation_id}")
    # Optional: Log the initial user input if available
    if callback_context.user_content:
        print(f" Initial User Input: {callback_context.user_content.parts[0].text}")

    # Returning None allows the agent execution to proceed normally
    return None

from .schema_and_tools import get_grouped_nutriments_from_open_food_facts

try:
    ingredients_generator_agent = Agent(
        name="ingredients_generator",
        model=model,
        instruction=INGREDIENTS_GENERATOR_INSTRUCTIONS,
        description=INGREDIENTS_GENERATOR_DESCRIPTION,
        tools=[get_grouped_nutriments_from_open_food_facts],
        output_key="ingredients_list_and_ailment",  # Save result to state
        before_agent_callback=before_ingredients_generator_callback,
    )
    print(f"✅ Agent '{ingredients_generator_agent.name}' created using model '{ingredients_generator_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Ingredients Generator agent. Error: {e}")
    ingredients_generator_agent = None