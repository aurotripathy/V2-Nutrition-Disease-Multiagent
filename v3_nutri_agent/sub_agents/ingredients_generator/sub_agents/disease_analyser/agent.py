import sys
import os
from google.adk.agents import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.agent_tool import AgentTool
from pydantic.types import T
from .prompts import DISEASE_ANALYSER_INSTRUCTIONS, DISEASE_ANALYSER_DESCRIPTION, get_disease_analyser_instruction
from .prompts import DISEASE_ANALYSER_SEARCH_AGENT_INSTRUCTIONS, DISEASE_ANALYSER_SEARCH_AGENT_DESCRIPTION, get_disease_analyser_search_agent_instruction
# Add project root to path for config import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from config import GEMINI_MODEL

model = GEMINI_MODEL

from google.adk.agents.callback_context import CallbackContext
from google.genai.types import Content
from typing import Optional

from google.adk.agents.invocation_context import InvocationContext

def before_disease_analyser_agent_callback(callback_context: CallbackContext) -> Optional[Content]:
    print(f"[B🤖CB]▶ Before_agent_callback triggered for agent: {callback_context.agent_name}")
    # print(f" Invocation ID: {callback_context.invocation_id}")
    # Optional: Log the initial user input if available
    print(f" <<< Ingredients list and ailment: {callback_context.session.state.get('ingredients_list_and_ailment')}")
    if callback_context.user_content:
        print(f" Initial User Input: {callback_context.user_content.parts[0].text}")
        
    # Returning None allows the agent execution to proceed normally
    return None

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content
from typing import Optional, Dict, Any
def before_disease_analyser_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
) -> Optional[Dict]:    
    print(f"[B🔧CB] Before_tool_callback triggered for tool: {tool.name}, args: {args} Tool Context - Agent Name: {tool_context.agent_name}")
    
    # Check if this is the search_for_diseases_agent AgentTool being invoked
    if tool.name == "search_for_diseases_agent":
        print(f"[B🔧CB] ========================================")
        print(f"[B🔧CB] search_for_diseases_agent AgentTool is being invoked")
        print(f"[B🔧CB] Arguments passed to the agent: {json.dumps(args, indent=2)}")
        print(f"[B🔧CB] ========================================")
        # Note: The actual google_search tool call within search_for_diseases_agent
        # won't trigger this callback - it's internal to that agent
    
    # Try to get from session state first (shared state)
    ingredients_data = None
    if hasattr(tool_context, 'session') and tool_context.session:
        ingredients_data = tool_context.session.state.get('ingredients_list_and_ailment')
        print(f" <<< Ingredients list and ailment from SESSION state: {ingredients_data}")
    else:
        # Fallback to tool_context.state (agent-local)
        ingredients_data = tool_context.state.get('ingredients_list_and_ailment')
        print(f" <<< Ingredients list and ailment from tool context state: {ingredients_data}")
    
    return None


### The Search Agent invoked as AgentTool
from google.adk.tools import google_search
import json

def before_search_for_diseases_agent_callback(callback_context: CallbackContext) -> Optional[Content]:
    """Callback to verify session state is accessible to search_for_diseases_agent."""
    print(f"[B🔍CB]▶ Before_agent_callback triggered for agent: {callback_context.agent_name}")
    print(f"[B🔍CB] ✅ search_for_diseases_agent IS being invoked")
    
    # Access session state to verify it's available
    session_state = callback_context.session.state
    ingredients_data = session_state.get('ingredients_list_and_ailment')

    print(f"[B🔍CB] Ingredients brought by the parent agent for analysis:\n```json\n{json.dumps(ingredients_data, indent=2)}\n```")
    
    if callback_context.user_content:
        print(f"[B🔍CB] User content/input to search_for_diseases_agent: {callback_context.user_content.parts[0].text}")
    
    return None

def before_search_for_diseases_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
) -> Optional[Dict]:
    """Callback to print what goes into the search tool."""
    print(f"[B🔍🔧CB] Before_tool_callback triggered for tool: {tool.name}")
    print(f"[B🔍🔧CB] Tool Context - Agent Name: {tool_context.agent_name}")
    
    # Print the actual search query with validation
    if 'query' in args:
        query = args['query']
        print(f"[B🔍🔧CB] ========================================")
        print(f"[B🔍🔧CB] ACTUAL SEARCH QUERY:")
        print(f"[B🔍🔧CB] {query}")
        print(f"[B🔍🔧CB] Query length: {len(query)} characters")
        print(f"[B🔍🔧CB] Query type: {type(query)}")
        if len(query) > 500:
            print(f"[B🔍🔧CB] ⚠️ WARNING: Query is very long ({len(query)} chars) - may cause API errors")
        if not query or not query.strip():
            print(f"[B🔍🔧CB] ⚠️ WARNING: Query is empty or whitespace only")
        print(f"[B🔍🔧CB] ========================================")
    else:
        print(f"[B🔍🔧CB] ⚠️ No 'query' parameter found in args")
        print(f"[B🔍🔧CB] All tool arguments:")
        print(f"[B🔍🔧CB] {json.dumps(args, indent=2)}")
    
    return None

search_for_diseases_agent = Agent(
  name="search_for_diseases_agent",
  model=model,    # --> Apply flash model for fast application and minimize token usage
  tools=[google_search],
  description="To do the actual search and analysis for diseases or health issues stemming from consuming the ingredients in the list provided",
  instruction=get_disease_analyser_search_agent_instruction,  # Use dynamic instruction function
  before_agent_callback=[before_search_for_diseases_agent_callback],  # Add callback to verify session state access
  before_tool_callback=[before_search_for_diseases_tool_callback],  # Print what goes into the search tool
  output_key="search_results",
)

def get_ingredients_list_and_ailment(tool_context: ToolContext) -> Optional[Dict]:
    # Try to get from session state first (shared state)
    ingredients_data = None
    if hasattr(tool_context, 'session') and tool_context.session:
        ingredients_data = tool_context.session.state.get('ingredients_list_and_ailment')
        print(f"[🔧C] Toolcall: Getting ingredients list from SESSION state: {ingredients_data}")
    else:
        # Fallback to tool_context.state (agent-local)
        ingredients_data = tool_context.state.get('ingredients_list_and_ailment')
        print(f"[🔧C] Toolcall: Getting ingredients list from tool context state: {ingredients_data}")
    
    return ingredients_data

disease_analyser_agent = Agent(
    name="disease_analyser_agent",
    model=model,
    tools=[AgentTool(agent=search_for_diseases_agent), get_ingredients_list_and_ailment],
    before_agent_callback=[before_disease_analyser_agent_callback],
    before_tool_callback=[before_disease_analyser_tool_callback],
    instruction=get_disease_analyser_instruction,  # Use dynamic instruction function
    description=DISEASE_ANALYSER_DESCRIPTION,
)