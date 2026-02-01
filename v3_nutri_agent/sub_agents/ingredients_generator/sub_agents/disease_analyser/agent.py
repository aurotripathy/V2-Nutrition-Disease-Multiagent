import sys
import os
from google.adk.agents import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.agent_tool import AgentTool
from pydantic.types import T
from .prompts import DISEASE_ANALYSER_INSTRUCTIONS, DISEASE_ANALYSER_DESCRIPTION
from .prompts import DISEASE_ANALYSER_SEARCH_AGENT_INSTRUCTIONS, DISEASE_ANALYSER_SEARCH_AGENT_DESCRIPTION
# Add project root to path for config import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from config import GEMINI_MODEL

model = GEMINI_MODEL

from google.adk.agents.callback_context import CallbackContext
from google.genai.types import Content
from typing import Optional


def before_disease_analyser_agent_callback(callback_context: CallbackContext) -> Optional[Content]:
    print(f"[B🤖CB]▶ Before_agent_callback triggered for agent: {callback_context.agent_name}")
    # print(f" Invocation ID: {callback_context.invocation_id}")
    # Optional: Log the initial user input if available
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
    tool_context: ToolContext
) -> Optional[Dict]:    
    print(f"[B🔧CB] Before_tool_callback triggered for tool: {tool.name}, args: {args} Tool Context - Agent Name: {tool_context.agent_name}")
    return None


### The Search Agent invoked as AgentTool
from google.adk.tools import google_search
search_for_diseases_agent = Agent(
  name="search_for_diseases_agent",
  model=model,    # --> Apply flash model for fast application and minimize token usage
  tools=[google_search],
  description="To do the actual search and analysis for diseases or health issues stemming from consuming the ingredients in the list provided",
  instruction=DISEASE_ANALYSER_SEARCH_AGENT_INSTRUCTIONS,
  output_key="search_results",
)



disease_analyser_agent = Agent(
    name="disease_analyser_agent",
    model=model,
    tools=[AgentTool(agent=search_for_diseases_agent)],
    before_agent_callback=[before_disease_analyser_agent_callback],
    before_tool_callback=[before_disease_analyser_tool_callback],
    instruction=DISEASE_ANALYSER_INSTRUCTIONS,
    description=DISEASE_ANALYSER_DESCRIPTION,
)