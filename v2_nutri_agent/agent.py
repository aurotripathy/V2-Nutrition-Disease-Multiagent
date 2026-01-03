"""
https://medium.com/@dharamai2024/structured-outputs-in-google-adk-part-3-of-the-series-80c683dc2d83
"""

from google.adk.agents import SequentialAgent, Agent, LlmAgent

from .util import load_instruction_from_file
from google.adk.tools import google_search
import google.adk
from pydantic import BaseModel, Field
from typing import Dict, Any
from .tools.get_nutriments_from_open_food_facts import get_grouped_nutriments_from_open_food_facts
import logging

from google.adk.tools.google_search_tool import GoogleSearchTool

logging.basicConfig(level=logging.DEBUG)

# Initialize the tool with the bypass parameter set to True
google_search_wrapper = GoogleSearchTool(bypass_multi_tools_limit=True)

logging.debug(f'adk version: {google.adk.__version__}')

fast_model = "gemini-2.5-flash"
model="gemini-2.5-pro"  # was flash
# model="gemini-2.5-flash"  # was flash

class IngredientsListAndAilment(BaseModel):
    food_item: str = Field(description="The food item name")
    ingredients: Dict[str, Dict[str, Any]] = Field(description="A dictionary of ingredients where each ingredient is a dictionary with 'value', 'unit', and optionally 'serving' keys")
    ailment: str = Field(description="Optionally, a disease or ailment that the users is interested in associating with the ingredients")


# --- Sub Agent 1: IngredientsGenerator ---
ingredients_generator_agent = LlmAgent(
    name="IngredientsGenerator",
    model=model,
    instruction=load_instruction_from_file("ingredients_generator_instructions.txt"),
    # tools=[get_nutriments_from_off, google_search],
    tools=[get_grouped_nutriments_from_open_food_facts],
    output_schema=IngredientsListAndAilment,
    output_key="ingredients_list_and_ailment",  # Save result to state
)

# --- Sub Agent 2: DiseaseIdentifier ---
disease_identifier_agent = LlmAgent(
    name="DiseaseIdentifier",
    model=model,
    instruction=load_instruction_from_file("disease_identifier_instructions.txt"),
    tools=[google_search],
)

from google.adk.agents.callback_context import CallbackContext
from typing import Optional, Dict, Any
from google.genai import types # For types.Content
from typing import Optional
from .util import load_greetings_from_file

def before_agent_greeting_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Checks if the user has been greeted. If not, greets them and skips agent execution.
    """
    if not callback_context.state.get("greeted"):
        callback_context.state["greeted"] = True
        # Return a Content object to immediately respond to the user and skip the LLM/tool
        return types.Content(
            parts=[types.Part(text=load_greetings_from_file("greetings_script.txt"))],
            role="model"
        )
    # Return None to allow the agent to proceed normally
    return None

# --- 3. Create the SequentialAgent ---
# This agent orchestrates the pipeline by running the sub-agents in order.
# has a built-in greeting agent
ingredients_x_disease_agent = SequentialAgent(
    name="IngredientsDiseasePipelineAgent",
    sub_agents=[
        # greetings_agent,
        ingredients_generator_agent,
        disease_identifier_agent,
    ],
    before_agent_callback=before_agent_greeting_callback, # Register the callback here
    description="Executes a sequence of ingredient search followed by disease identification stemming from those ingredients.",
)

# For ADK tools compatibility, the root agent must be named `root_agent`.
root_agent = ingredients_x_disease_agent
