from google.adk.agents import Agent
from .schema_and_tools import get_grouped_nutriments_from_open_food_facts
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.agent_tool import AgentTool
from .prompts import INGREDIENTS_GENERATOR_INSTRUCTIONS, INGREDIENTS_GENERATOR_DESCRIPTION
from .prompts import SEARCH_AGENT_INSTRUCTIONS, SEARCH_AGENT_DESCRIPTION
import sys
import os
# Add project root to path for config import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from config import MODEL_GEMINI_2_5_FLASH

model = MODEL_GEMINI_2_5_FLASH
google_search_tool = GoogleSearchTool(bypass_multi_tools_limit=True)


from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content
from typing import Optional, Dict, Any

def before_ingredients_generator_callback(callback_context: CallbackContext) -> Optional[Content]:
    print(f"[B🤖CB]▶ Before_agent_callback triggered for agent: {callback_context.agent_name}")
    # print(f" Invocation ID: {callback_context.invocation_id}")
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
    print(f"[B🔧CB] Before_tool_callback triggered for tool: {tool.name}, args: {args} Tool Context - Agent Name: {tool_context.agent_name}")
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


def after_ingredients_generator_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_response: Any,
    tool_context: ToolContext
) -> Optional[Dict]:
    """
    Callback function that prints the output after a tool execution completes.
    
    Specifically prints the output of the Open Food Facts (OFF) API call.
    
    Returns:
        None: Use the tool's actual result.
        Dict: Override the result with this value instead.
    """
    print(f"[A🔧BC] After_tool_callback triggered for tool: {tool.name} in agent: {tool_context.agent_name}")

    tool_context.state['ingredients_list_and_ailment'] = tool_response
    
    # Check if this is the OFF API tool call
    if tool.name == "get_grouped_nutriments_from_open_food_facts":
        print(f"[T] [OFF API OUTPUT] Food item searched: {args.get('food_item', 'N/A')}")
        print(f"[T] [OFF API OUTPUT] Result type: {type(tool_response)}")
        
        # Print the result - handle both dict and other types
        if isinstance(tool_response, dict):
            if not tool_response:
                print("[T] [OFF API OUTPUT] Result: Empty dictionary (no nutriments found)")
            else:
                print(f"[T] [OFF API OUTPUT] Result: Found {len(tool_response)} nutrient groups")
                print("[T] [OFF API OUTPUT] Nutrient groups:")
                for nutrient_name, nutrient_data in tool_response.items():
                    print(f"   - {nutrient_name}: {nutrient_data}")
        else:
            print(f"[T] [OFF API OUTPUT] Result: {tool_response}")
    else:
        # For other tools, just print a summary
        print(f"[T] [TOOL OUTPUT] Tool '{tool.name}' returned: {type(tool_response)}")
        if isinstance(tool_response, dict) and tool_response:
            print(f"   Result keys: {list(tool_response.keys())}")
        elif isinstance(tool_response, str):
            print(f"   Result preview: {tool_response[:200]}..." if len(str(tool_response)) > 200 else f"   Result: {tool_response}")
    
    # Return None to use the tool's actual result
    return None

# --- 2. Create a fallback function that the LLM can call if the first one fails ---
# We can just use the pre-built GoogleSearchTool directly as a function


### The Search Agent
from google.adk.tools import google_search
search_ingredients_agent = Agent(
  name="search_ingredients_agent",
  model=model,    # --> Apply flash model for fast application and minimize token usage
  description="To do the actual search and analysis for ingredients based on food_item",
  tools=[google_search],
  instruction=SEARCH_AGENT_INSTRUCTIONS,
  output_key="search_results",
)

from .schema_and_tools import get_grouped_nutriments_from_open_food_facts
from .sub_agents.disease_analyser.agent import disease_analyser_agent

try:
    ingredients_generator_agent = Agent(
        name="ingredients_generator",
        model=model,
        instruction=INGREDIENTS_GENERATOR_INSTRUCTIONS,
        description=INGREDIENTS_GENERATOR_DESCRIPTION,
        tools=[get_grouped_nutriments_from_open_food_facts,  AgentTool(agent=search_ingredients_agent)],
        before_tool_callback=before_ingredients_generator_tool_callback,
        after_tool_callback=after_ingredients_generator_tool_callback,
        output_key="ingredients_list_and_ailment",  # Save result to state
        before_agent_callback=[before_ingredients_generator_callback],
        disallow_transfer_to_parent=True,
        sub_agents=[disease_analyser_agent],
    )
    print(f"✅ Agent '{ingredients_generator_agent.name}' created using model '{ingredients_generator_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Ingredients Generator agent. Error: {e}")
    ingredients_generator_agent = None