from google.adk.agents import Agent
from .schema_and_tools import say_hello
from .prompts import GREETING_HANDLER_INSTRUCTION, GREETING_HANDLER_DESCRIPTION
import sys
import os
# Add project root to path for config import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from config import MODEL_GEMINI_2_5_FLASH

model = MODEL_GEMINI_2_5_FLASH
try:
    greeting_handler_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model = MODEL_GEMINI_2_5_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="greeting_handler_agent",
        instruction=GREETING_HANDLER_INSTRUCTION,
        description=GREETING_HANDLER_DESCRIPTION,
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_handler_agent.name}' created using model '{greeting_handler_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({greeting_handler_agent.model}). Error: {e}")
