
from google.adk.agents import Agent
from .schema_and_tools import say_goodbye
from .prompts import FAREWELL_HANDLER_INSTRUCTION, FAREWELL_HANDLER_DESCRIPTION
import sys
import os
# Add project root to path for config import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from config import GEMINI_MODEL

model = GEMINI_MODEL


from google.adk.agents.callback_context import CallbackContext
from google.genai.types import Content
from typing import Optional

def before_farewell_handler_callback(callback_context: CallbackContext) -> Optional[Content]:
    print(f"▶ Entering Agent: {callback_context.agent_name}")
    print(f" Invocation ID: {callback_context.invocation_id}")
    # Optional: Log the initial user input if available
    if callback_context.user_content:
        print(f" Initial User Input: {callback_context.user_content.parts[0].text}")

    # Returning None allows the agent execution to proceed normally
    return None


try:
    farewell_handler_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model = GEMINI_MODEL,
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="farewell_handler",
        instruction=FAREWELL_HANDLER_INSTRUCTION,
        description=FAREWELL_HANDLER_DESCRIPTION,
        tools=[say_goodbye],
        before_agent_callback=before_farewell_handler_callback,
    )
    print(f"✅ Agent '{farewell_handler_agent.name}' created using model '{farewell_handler_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Farewell handler agent. Check API Key ({farewell_handler_agent.model}). Error: {e}")