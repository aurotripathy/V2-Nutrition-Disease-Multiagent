from google.adk.agents import Agent
# from .open_food_facts_tools import get_grouped_nutriments_from_open_food_facts
from .ocr_processing_tools import get_nutriments_from_OCRd_image_file
from .open_food_facts_tools import get_nutriments_from_open_food_facts
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
from config import GEMINI_MODEL

model = GEMINI_MODEL
google_search_tool = GoogleSearchTool(bypass_multi_tools_limit=True)


from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content
from typing import Optional, Dict, Any

def before_agent_callback_ingredients_generator_agent(callback_context: CallbackContext) -> Optional[Content]:
    print(f"[Bf🤖CB] Before_agent_callback triggered for agent: {callback_context.agent_name}")
    # print(f" Invocation ID: {callback_context.invocation_id}")
    # Optional: Log the initial user input if available
    if callback_context.user_content:
        print(f" Initial User Input: {callback_context.user_content.parts[0].text}")
    
    # Returning None allows the agent execution to proceed normally
    return None


def after_agent_callback_ingredients_generator_agent(callback_context: CallbackContext) -> Optional[Content]:
    print(f"[Af🤖CB] After_agent_callback triggered for agent: {callback_context.agent_name}")
    # print(f" Invocation ID: {callback_context.invocation_id}")
    # Optional: Log the initial user input if available
    if callback_context.user_content:
        print(f" Initial User Input: {callback_context.user_content.parts[0].text}")
    
    # Check if ingredients_list_and_ailment is in session state (saved by tool callbacks or output_key)
    session_state = callback_context.session.state
    if 'ingredients_list_and_ailment' in session_state:
        data = session_state.get('ingredients_list_and_ailment')
        print(f"[Af🤖CB] ✅ ingredients_list_and_ailment found in session state")
        print(f"[Af🤖CB] Data type: {type(data)}")
        if isinstance(data, dict):
            print(f"[Af🤖CB] Data keys: {list(data.keys()) if data else 'empty dict'}")
        else:
            print(f"[Af🤖CB] Data preview: {str(data)[:100]}...")
    else:
        print(f"[Af🤖CB] ⚠️ ingredients_list_and_ailment NOT found in session state")
        # Try to get from agent response if available
        if hasattr(callback_context, 'agent_response') and callback_context.agent_response:
            response_data = callback_context.agent_response
            if isinstance(response_data, dict):
                session_state['ingredients_list_and_ailment'] = response_data
                print(f"[Af🤖CB] ✅ Saved agent response to session state as fallback")
        # The output_key should have saved the agent's final response
        # If it's not there, the agent might not have returned the ingredients data
    
    # CRITICAL: Ensure data is in state before any transfer happens
    # Re-verify and re-save to ensure it's accessible to sub-agents
    if 'ingredients_list_and_ailment' in session_state:
        data = session_state.get('ingredients_list_and_ailment')
        # Force save again to ensure it's persisted
        session_state['ingredients_list_and_ailment'] = data
        print(f"[Af🤖CB] 🔒 Re-verified and re-saved ingredients_list_and_ailment to ensure sub-agent access")
        print(f"[Af🤖CB] 🔒 State object ID: {id(session_state)}")
        print(f"[Af🤖CB] 🔒 Session object ID: {id(callback_context.session)}")
    
    # Returning None allows the agent execution to proceed normally
    return None

def before_tool_callback_ingredients_generator_agent(
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
    print(f"[Bf🔧CB] Before_tool_callback triggered for tool: {tool.name}, args: {args} Tool Context - Agent Name: {tool_context.agent_name}")
    return None


def after_tool_callback_ingredients_generator_agent(
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
    print(f"[Af🔧CB] After_tool_callback triggered for tool: {tool.name}, args: {args} Tool Context - Agent Name: {tool_context.agent_name}")

    print(f"[Af🔧CB] Tool response: {tool_response}")
    
    # Check if this is the OFF API tool call. there are two tools that can be called: get_nutriments_from_open_food_facts and get_nutriments_from_OCRd_image_file
    if tool.name == "get_grouped_nutriments_from_open_food_facts":
        print(f"[T] [OFF API OUTPUT] Food item searched: {args.get('food_item', 'N/A')}")
        print(f"[T] [OFF API OUTPUT] Result type: {type(tool_response)}")
        
        # Print the result - handle both dict and other types
        if isinstance(tool_response, dict):
            if not tool_response:
                print("[T] ⚠️ [OFF API OUTPUT] Result: Empty dictionary (no nutriments found)")
            else:
                # Format the data according to the expected structure: {"ingredients": {...}, "ailment": "..."}
                # For now, use the tool_response as ingredients (it's already a dict of ingredients)
                # The ailment will be extracted by the agent from user input
                formatted_data = tool_response  # The tool_response IS the ingredients dict
                
                # CRITICAL: Save to session state - use the session from tool_context
                # The tool_context should have access to the session
                session = None
                if hasattr(tool_context, 'session') and tool_context.session:
                    session = tool_context.session
                elif hasattr(tool_context, 'invocation_context'):
                    inv_context = tool_context.invocation_context
                    if hasattr(inv_context, 'session'):
                        session = inv_context.session
                
                if session:
                    session.state['ingredients_list_and_ailment'] = formatted_data
                    print(f">>> ✅ Saved ingredients_list_and_ailment to session.state")
                    print(f">>> [STATE] Session ID: {id(session)}")
                    print(f">>> [STATE] State object ID: {id(session.state)}")
                    print(f">>> [STATE] Verification: {session.state.get('ingredients_list_and_ailment') is not None}")
                    print(f">>> [STATE] Data keys: {list(formatted_data.keys())[:5]}..." if isinstance(formatted_data, dict) else "Not a dict")
                else:
                    print(f">>> ⚠️ Could not find session object in tool_context")
                
                # Also save to tool_context.state as fallback
                tool_context.state['ingredients_list_and_ailment'] = formatted_data
                print(f">>> ✅ Also saved to tool_context.state as fallback")
                
                print(f"[T] [OFF API OUTPUT] Result: Found {len(tool_response)} nutrient groups")
                print("[T] [OFF API OUTPUT] Nutrient groups:")
                for nutrient_name, nutrient_data in tool_response.items():
                    print(f"   - {nutrient_name}: {nutrient_data}")
        else:
            print(f"[T] [OFF API OUTPUT] Result: {tool_response}")
    elif tool.name == "search_ingredients_agent":
        # Handle search_ingredients_agent (AgentTool) response
        print(f"[T] [SEARCH_AGENT OUTPUT] Tool: {tool.name}")
        print(f"[T] [SEARCH_AGENT OUTPUT] Result type: {type(tool_response)}")
        
        if isinstance(tool_response, dict) and tool_response:
            # Save to session state - ensure we save to the actual session
            if hasattr(tool_context, 'session') and tool_context.session:
                tool_context.session.state['ingredients_list_and_ailment'] = tool_response
                print(f">>> ✅ Saved ingredients_list_and_ailment to tool_context.session.state from search_ingredients_agent")
                print(f">>> [STATE] Verification: {tool_context.session.state.get('ingredients_list_and_ailment') is not None}")
            
            # Also save to tool_context.state
            tool_context.state['ingredients_list_and_ailment'] = tool_response
            print(f">>> ✅ Also saved to tool_context.state from search_ingredients_agent")
            
            # Also try invocation context
            try:
                if hasattr(tool_context, 'invocation_context'):
                    inv_context = tool_context.invocation_context
                    if hasattr(inv_context, 'session'):
                        inv_context.session.state['ingredients_list_and_ailment'] = tool_response
                        print(f">>> ✅ Also saved via invocation_context.session.state from search_ingredients_agent")
            except Exception as e:
                print(f">>> [STATE] Could not access via invocation_context: {e}")
            
            print(f"[T] [SEARCH_AGENT OUTPUT] Result keys: {list(tool_response.keys())}")
        else:
            print(f"[T] [SEARCH_AGENT OUTPUT] Result: {tool_response}")
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


### 🤖🔍 The Search Agent
from google.adk.tools import google_search

def after_agent_callback_search_ingredients_agent(callback_context: CallbackContext) -> Optional[Content]:
    """
    Callback function that handles the output after search_ingredients_agent completes.
    
    Verifies that ingredients data is in session state (saved by after_tool_callback).
    """
    print(f"[Af🔍🤖CB] After_agent_callback triggered for agent: {callback_context.agent_name}")
    
    # Check if ingredients data is in session state (should have been saved by after_tool_callback)
    session_state = callback_context.session.state
    
    if 'ingredients_list_and_ailment' in session_state:
        data = session_state.get('ingredients_list_and_ailment')
        print(f"[Af🔍🤖CB] ✅ ingredients_list_and_ailment found in session state")
        print(f"[Af🔍🤖CB] Data type: {type(data)}")
        if isinstance(data, dict):
            print(f"[Af🔍🤖CB] Data keys: {list(data.keys()) if data else 'empty dict'}")
    else:
        print(f"[Af🔍🤖CB] ⚠️ ingredients_list_and_ailment NOT found in session state")
        print(f"[Af🔍🤖CB] Note: Data should have been saved by after_search_ingredients_agent_tool_callback")
    
    return None

def after_tool_callback_search_ingredients_agent(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_response: Any,
    tool_context: ToolContext
) -> Optional[Dict]:
    """
    Callback function that handles the output after search_ingredients_agent's tools execute.
    
    Specifically handles when search_ingredients_agent (as an AgentTool) returns data.
    Saves the response directly to session state (no global variable needed).
    """
    print(f"[Af🔧CB] [SEARCH_AGENT] After_tool_callback triggered for tool: {tool.name}")
    print(f"[Af🔧CB] [SEARCH_AGENT] Response type: {type(tool_response)}")
    
    # Save the response to session state if it's valid ingredients data
    if isinstance(tool_response, dict) and tool_response:
        # Save directly to session state (no need for global variable)
        if hasattr(tool_context, 'session') and tool_context.session:
            tool_context.session.state['ingredients_list_and_ailment'] = tool_response
            print(f"[Af🔧CB] [SEARCH_AGENT] ✅ Saved ingredients_list_and_ailment to tool_context.session.state")
            print(f"[Af🔧CB] [SEARCH_AGENT] Verification: {tool_context.session.state.get('ingredients_list_and_ailment') is not None}")
        else:
            # Fallback to tool_context.state
            tool_context.state['ingredients_list_and_ailment'] = tool_response
            print(f"[Af🔧CB] [SEARCH_AGENT] ✅ Saved ingredients_list_and_ailment to tool_context.state")
            print(f"[Af🔧CB] [SEARCH_AGENT] Verification: {tool_context.state.get('ingredients_list_and_ailment') is not None}")
        
        print(f"[Af🔧CB] [SEARCH_AGENT] Data keys: {list(tool_response.keys()) if isinstance(tool_response, dict) else 'N/A'}")
    else:
        print(f"[Af🔧CB] [SEARCH_AGENT] ⚠️ Response is not a valid dict or is empty")
    
    return None

search_ingredients_agent = Agent(
  name="search_ingredients_agent",
  model=model,    # --> Apply flash model for fast application and minimize token usage
  description="To do the actual search and analysis for ingredients based on food_item",
  tools=[google_search],
  instruction=SEARCH_AGENT_INSTRUCTIONS,
  after_agent_callback=[after_agent_callback_search_ingredients_agent],
  after_tool_callback=[after_tool_callback_search_ingredients_agent],
#   output_key="search_results",
)


from .open_food_facts_tools import get_grouped_nutriments_from_open_food_facts
from .sub_agents.disease_analyser.agent import disease_analyser_agent

try:
    # 🤖 The Ingredients Generator Agent
    ingredients_generator_agent = Agent(
        name="ingredients_generator_agent",
        model=model,
        instruction=INGREDIENTS_GENERATOR_INSTRUCTIONS,
        description=INGREDIENTS_GENERATOR_DESCRIPTION,
        tools=[get_nutriments_from_OCRd_image_file,  
            get_grouped_nutriments_from_open_food_facts,
            AgentTool(agent=search_ingredients_agent)
        ],
        before_tool_callback=before_tool_callback_ingredients_generator_agent,
        after_tool_callback=after_tool_callback_ingredients_generator_agent,
        output_key="ingredients_list_and_ailment",  # Save agent's final output to session state
        before_agent_callback=[before_agent_callback_ingredients_generator_agent],
        after_agent_callback=[after_agent_callback_ingredients_generator_agent],
        disallow_transfer_to_parent=True,
        sub_agents=[disease_analyser_agent],
    )
    print(f"✅ Agent '{ingredients_generator_agent.name}' created using model '{ingredients_generator_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Ingredients Generator agent. Error: {e}")
    ingredients_generator_agent = None