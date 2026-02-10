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
    print(f"[Bf🤖CB]▶ Before_agent_callback triggered for agent: {callback_context.agent_name}")
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
    print(f"[Bf🔧CB] Before_tool_callback triggered for tool: {tool.name}, args: {args} Tool Context - Agent Name: {tool_context.agent_name}")
    
    # Check if this is the search_for_diseases_agent AgentTool being invoked
    if tool.name == "search_for_diseases_agent":
        print(f"[Bf🔧CB] ========================================")
        print(f"[Bf🔧CB] search_for_diseases_agent AgentTool is being invoked")
        print(f"[Bf🔧CB] Arguments passed to the agent: {json.dumps(args, indent=2)}")
        print(f"[Bf🔧CB] ========================================")
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
    print(f"[Bf🤖CB] Before_agent_callback triggered for agent: {callback_context.agent_name}")
    
    # Access session state to verify it's available
    session_state = callback_context.session.state
    ingredients_data = session_state.get('ingredients_list_and_ailment')

    print(f"[Bf🤖CB] Ingredients brought in by the parent agent for analysis:\n```json\n{json.dumps(ingredients_data, indent=2)}\n```")
    
    if callback_context.user_content:
        print(f"[Bf🤖CB] User content/input to search_for_diseases_agent: {callback_context.user_content.parts[0].text}")
    
    return None

def before_search_for_diseases_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
) -> Optional[Dict]:
    """Callback to print and validate what goes into the search tool."""
    print(f"[Bf🔍🔧CB] Before_tool_callback triggered for tool: {tool.name} in agent: {tool_context.agent_name}")
    
    # Print the actual search query with validation
    if 'query' in args:
        query = args['query']
        print(f"[Bf🔍🔧CB] ========================================")
        print(f"[Bf🔍🔧CB] ACTUAL SEARCH QUERY:")
        print(f"[Bf🔍🔧CB] {query}")
        print(f"[Bf🔍🔧CB] Query length: {len(query)} characters")
        print(f"[Bf🔍🔧CB] Query type: {type(query)}")
        
        # Validation and error prevention
        if not query or not query.strip():
            print(f"[Bf🔍🔧CB] ⚠️ ERROR: Query is empty or whitespace only - blocking call")
            return {
                "error": "Search query is empty. Please provide a valid search query.",
                "status": "error"
            }
        
        # Truncate very long queries to prevent 500 errors
        MAX_QUERY_LENGTH = 200  # Reasonable limit for search queries
        if len(query) > MAX_QUERY_LENGTH:
            print(f"[Bf🔍🔧CB] ⚠️ WARNING: Query is very long ({len(query)} chars) - truncating to {MAX_QUERY_LENGTH} chars")
            truncated_query = query[:MAX_QUERY_LENGTH].rsplit(' ', 1)[0]  # Truncate at word boundary
            args['query'] = truncated_query
            print(f"[Bf🔍🔧CB] Truncated query: {truncated_query}")
        
        print(f"[Bf🔍🔧CB] ========================================")
    else:
        print(f"[Bf🔍🔧CB] ⚠️ No 'query' parameter found in args")
        print(f"[Bf🔍🔧CB] All tool arguments:")
        print(f"[Bf🔍🔧CB] {json.dumps(args, indent=2)}")
    
    return None  # Return None to proceed with the call (with potentially modified args)

def after_search_for_diseases_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_response: Any,
    tool_context: ToolContext,
) -> Optional[Dict]:
    """Callback to handle errors and responses from the search tool."""
    print(f"[Af🔍🔧CB] After_tool_callback triggered for tool: {tool.name} in agent: {tool_context.agent_name}")
    
    # Check if the response indicates an error
    if isinstance(tool_response, dict):
        if 'error' in tool_response:
            error_code = tool_response.get('error', {}).get('code', 'UNKNOWN')
            error_message = tool_response.get('error', {}).get('message', 'Unknown error')
            error_status = tool_response.get('error', {}).get('status', 'UNKNOWN')
            
            print(f"[Af🔍🔧CB] ⚠️ ERROR DETECTED:")
            print(f"[Af🔍🔧CB]   Code: {error_code}")
            print(f"[Af🔍🔧CB]   Status: {error_status}")
            print(f"[Af🔍🔧CB]   Message: {error_message}")
            
            # Handle 500 INTERNAL errors specifically
            if error_code == 500 or error_status == 'INTERNAL':
                print(f"[Af🔍🔧CB] 🔄 Handling 500 INTERNAL error - returning graceful error message")
                # Return a user-friendly error message instead of crashing
                return {
                    "error": "The search service encountered an internal error. Please try again or rephrase your search query.",
                    "status": "error",
                    "original_error": error_message
                }
            # Handle other errors
            elif error_code == 400:
                print(f"[Af🔍🔧CB] ⚠️ Bad request error - query may be invalid")
                return {
                    "error": "Invalid search query. Please check the query format.",
                    "status": "error"
                }
            elif error_code == 429:
                print(f"[Af🔍🔧CB] ⚠️ Rate limit error - too many requests")
                return {
                    "error": "Too many search requests. Please wait a moment and try again.",
                    "status": "error"
                }
    
    # If no error, return None to use the actual response
    print(f"[Af🔍🔧CB] ✅ Tool response received successfully")
    return None

search_for_diseases_agent = Agent(
  name="search_for_diseases_agent",
  model=model,    # --> Apply flash model for fast application and minimize token usage
  tools=[google_search],
  description="To do the actual search and analysis for diseases or health issues stemming from consuming the ingredients in the list provided",
  instruction=get_disease_analyser_search_agent_instruction,  # Use dynamic instruction function
  before_agent_callback=[before_search_for_diseases_agent_callback],  # Add callback to verify session state access
  before_tool_callback=[before_search_for_diseases_tool_callback],  # Print and validate what goes into the search tool
  after_tool_callback=[after_search_for_diseases_tool_callback],  # Handle errors from the search tool
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
    # as a check, print the tool context state
    print(f"[🔧C] Toolcall: Tool context state: {tool_context.state}")

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