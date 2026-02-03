from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext

from .tools import read_update_name_from_state, get_user_name

  
from google.adk.agents import Agent
from .prompt import FAREWELL_AGENT_INSTRUCTION
farewell_agent = Agent(
    model="gemini-2.5-flash",
    name="farewell_agent",
    instruction=FAREWELL_AGENT_INSTRUCTION,
    before_agent_callback=[read_update_name_from_state],
    tools=[get_user_name],
)