import sys
import os
from google.adk.agents import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.agent_tool import AgentTool
from .prompts import get_disease_analyser_agent_instruction, get_search_for_diseases_agent_instruction
from .prompts import DISEASE_ANALYSER_DESCRIPTION, DISEASE_ANALYSER_SEARCH_AGENT_DESCRIPTION

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

def before_agent_callback_disease_analyser_agent(callback_context: CallbackContext) -> Optional[Content]:
    print(f"[Bf🤖CB] Before_agent_callback triggered for agent: {callback_context.agent_name}")
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

def before_tool_callback_disease_analyser_agent(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
) -> Optional[Dict]:    

    
    # Check if this is the search_for_diseases_agent AgentTool being invoked
    if tool.name == "search_for_diseases_agent":
        print(f"[Bf🔧CB] ========================================")
        print(f"[Bf🔧CB] search_for_diseases_agent AgentTool is being invoked")
        print(f"[Bf🔧CB] Arguments passed to the agent: ```json\n{json.dumps(args)}\n```")
        
        # Get ingredients from session state for logging
        ingredients_data = None
        if hasattr(tool_context, 'session') and tool_context.session:
            ingredients_data = tool_context.session.state.get('ingredients_list_and_ailment')
        else:
            ingredients_data = tool_context.state.get('ingredients_list_and_ailment')
        
        if ingredients_data and isinstance(ingredients_data, dict):
            all_ingredient_names = list(ingredients_data.keys())
            print(f"[Bf🔧CB] Found {len(all_ingredient_names)} total ingredients in session state")
            print(f"[Bf🔧CB] Note: Ingredients will be injected into the search query by before_tool_callback_search_for_diseases_agent")
        else:
            print(f"[Bf🔧CB] ⚠️ No ingredients data found in session state")
        
        print(f"[Bf🔧CB] ========================================")
        # Note: The actual google_search tool call within search_for_diseases_agent
        # won't trigger this callback - it's internal to that agent
        # Ingredients are injected into the search query in before_tool_callback_search_for_diseases_agent
    
    return None


### The Search Agent invoked as AgentTool
from google.adk.tools import google_search
import json

def before_agent_callback_search_for_diseases_agent(callback_context: CallbackContext) -> Optional[Content]:
    """Callback to verify session state is accessible to search_for_diseases_agent."""
    print(f"[Bf🤖CB] Before_agent_callback triggered for agent: {callback_context.agent_name}")
    
    # Access session state to verify it's available
    session_state = callback_context.session.state
    ingredients_data = session_state.get('ingredients_list_and_ailment')

    print(f"[Bf🤖CB] Ingredients brought in to the disease analyser agent for analysis:\n```json\n{json.dumps(ingredients_data)}\n```")
    
    if callback_context.user_content:
        print(f"[Bf🤖CB] User content/input to search_for_diseases_agent: {callback_context.user_content.parts[0].text}")
    
    return None

def before_tool_callback_search_for_diseases_agent(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
) -> Optional[Dict]:
    """Callback to print and validate what goes into the search tool, and inject ingredients."""
    print(f"[Bf🔍🔧CB] Before_tool_callback triggered for tool: {tool.name} in agent: {tool_context.agent_name}")
    
    # Get ingredients from session state
    ingredients_data = None
    if hasattr(tool_context, 'session') and tool_context.session:
        ingredients_data = tool_context.session.state.get('ingredients_list_and_ailment')
    else:
        ingredients_data = tool_context.state.get('ingredients_list_and_ailment')
    
    # Extract ingredient names from the ingredients_data dict
    ingredient_names = []
    if ingredients_data and isinstance(ingredients_data, dict):
        ingredient_names = list(ingredients_data.keys())
        print(f"[Bf🔍🔧CB] Found {len(ingredient_names)} ingredients in session state")
    
    # Print the actual search query with validation
    if 'query' in args:
        query = args['query']
        print(f"[Bf🔍🔧CB] ========================================")
        print(f"[Bf🔍🔧CB] ORIGINAL SEARCH QUERY:")
        print(f"[Bf🔍🔧CB] {query}")
        
        # Inject ingredients into the search query (smart injection to prevent query length issues)
        if ingredient_names:
            # Limit to first 10 ingredients to prevent query from becoming too long
            MAX_INGREDIENTS_TO_INCLUDE = 10
            ingredients_to_include = ingredient_names[:MAX_INGREDIENTS_TO_INCLUDE]
            
            # Create a compact string of ingredient names
            ingredients_str = ", ".join(ingredients_to_include)
            
            # If there are more ingredients, add a note
            if len(ingredient_names) > MAX_INGREDIENTS_TO_INCLUDE:
                remaining_count = len(ingredient_names) - MAX_INGREDIENTS_TO_INCLUDE
                ingredients_str += f" and {remaining_count} more"
            
            # Append to the query
            enhanced_query = f"{query} AND ingredients:{ingredients_str}"
            print(f"[Bf🔍🔧CB] ENHANCED SEARCH QUERY (with {len(ingredients_to_include)}/{len(ingredient_names)} ingredients):")
            print(f"[Bf🔍🔧CB] {enhanced_query}")
            args['query'] = enhanced_query
            query = enhanced_query  # Update for validation below
        else:
            print(f"[Bf🔍🔧CB] ⚠️ No ingredients found in session state - using original query")
        
        print(f"[Bf🔍🔧CB] Query length: {len(query)} characters")
        print(f"[Bf🔍🔧CB] Query type: {type(query)}")
        
        # Validation and error prevention
        if not query or not query.strip():
            print(f"[Bf🔍🔧CB] ⚠️ ERROR: Query is empty or whitespace only - blocking call")
            return {
                "error": "Search query is empty. Please provide a valid search query.",
                "status": "error"
            }
        
        # Final truncation check to prevent 500 errors
        MAX_QUERY_LENGTH = 200  # Reasonable limit for search queries
        if len(query) > MAX_QUERY_LENGTH:
            print(f"[Bf🔍🔧CB] ⚠️ WARNING: Query is very long ({len(query)} chars) - truncating to {MAX_QUERY_LENGTH} chars")
            truncated_query = query[:MAX_QUERY_LENGTH].rsplit(' ', 1)[0]  # Truncate at word boundary
            args['query'] = truncated_query
            print(f"[Bf🔍🔧CB] Truncated query: {truncated_query}")
            query = truncated_query
        
        print(f"[Bf🔍🔧CB] ========================================")
    else:
        print(f"[Bf🔍🔧CB] ⚠️ No 'query' parameter found in args")
        print(f"[Bf🔍🔧CB] All tool arguments:")
        print(f"[Bf🔍🔧CB] {json.dumps(args, indent=2)}")
    
    return None  # Return None to proceed with the call (with potentially modified args)

def after_tool_callback_search_for_diseases_agent(
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
  description=DISEASE_ANALYSER_SEARCH_AGENT_DESCRIPTION,
  instruction=get_search_for_diseases_agent_instruction,  # Use dynamic instruction function
  before_agent_callback=[before_agent_callback_search_for_diseases_agent],  # Add callback to verify session state access
  before_tool_callback=[before_tool_callback_search_for_diseases_agent],  # Print and validate what goes into the search tool
  after_tool_callback=[after_tool_callback_search_for_diseases_agent],  # Handle errors from the search tool
  output_key="search_results",
)

disease_analyser_agent = Agent(
    name="disease_analyser_agent",
    model=model,
    tools=[AgentTool(agent=search_for_diseases_agent)],
    before_agent_callback=[before_agent_callback_disease_analyser_agent],
    before_tool_callback=[before_tool_callback_disease_analyser_agent], # Print and validate what goes into the search tool, and inject ingredients
    instruction=get_disease_analyser_agent_instruction,  # Use dynamic instruction function
    description=DISEASE_ANALYSER_DESCRIPTION,
)