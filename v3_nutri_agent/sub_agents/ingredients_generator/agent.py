from google.adk.agents import Agent
from .schema_and_tools import get_grouped_nutriments_from_open_food_facts
from google.adk.tools.google_search_tool import GoogleSearchTool
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
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content
from typing import Optional, Dict, Any

def before_ingredients_generator_callback(callback_context: CallbackContext) -> Optional[Content]:
    print(f"▶ Entering Agent: {callback_context.agent_name}")
    print(f" Invocation ID: {callback_context.invocation_id}")
    # Optional: Log the initial user input if available
    if callback_context.user_content:
        print(f" Initial User Input: {callback_context.user_content.parts[0].text}")

    # Returning None allows the agent execution to proceed normally
    return None


def before_ingredients_generator_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict]:
    """
    Callback function that prints all information when a tool is invoked.
    
    Checks if the tool call is allowed based on specific business rules.
    
    Returns:
        None: Proceed with normal tool execution.
        Dict: Skip execution and return this result instead.
    """
    print(f"▶ before_tool_callback triggered for tool: {tool.name}, args: {args} Tool Context - Agent Name: {tool_context.agent_name}")
    # print(f"   Tool Context - Invocation ID: {tool_context.invocation_id}")
    
    # Print user content if available
    # if tool_context.user_content:
    #     print(f"   Tool Context - User Content:")
    #     if tool_context.user_content.parts:
    #         for i, part in enumerate(tool_context.user_content.parts):
    #             print(f"     Part {i}: {part.text if hasattr(part, 'text') else part}")
    
    # Print all available attributes in tool_context
    # print(f"   Available attributes in tool_context:")
    # for attr in dir(tool_context):
    #     if not attr.startswith('_'):
    #         try:
    #             value = getattr(tool_context, attr)
    #             if not callable(value):
    #                 print(f"     {attr}: {value}")
    #         except Exception:
    #             pass
    
    # Example guardrail: You can add business logic here
    # if tool.name == "get_grouped_nutriments_from_open_food_facts" and args.get("food_item", "").lower() == "restricted_item":
    #     print("🚫 Guardrail activated: Blocking tool call for restricted item.")
    #     return {
    #         "status": "error",
    #         "message": "Policy violation: This item is restricted."
    #     }
    
    # Return None to allow the normal tool function to execute
    return None

# --- 2. Create a fallback function that the LLM can call if the first one fails ---
# We can just use the pre-built GoogleSearchTool directly as a function
google_search_tool = GoogleSearchTool(bypass_multi_tools_limit=True)
from .schema_and_tools import get_grouped_nutriments_from_open_food_facts

try:
    ingredients_generator_agent = Agent(
        name="ingredients_generator",
        model=model,
        instruction=INGREDIENTS_GENERATOR_INSTRUCTIONS,
        description=INGREDIENTS_GENERATOR_DESCRIPTION,
        tools=[get_grouped_nutriments_from_open_food_facts, google_search_tool],
        before_tool_callback=before_ingredients_generator_tool_callback,
        output_key="ingredients_list_and_ailment",  # Save result to state
        before_agent_callback=[before_ingredients_generator_callback],
    )
    print(f"✅ Agent '{ingredients_generator_agent.name}' created using model '{ingredients_generator_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Ingredients Generator agent. Error: {e}")
    ingredients_generator_agent = None