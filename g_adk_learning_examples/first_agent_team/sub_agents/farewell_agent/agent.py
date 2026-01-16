from google.adk.agents import Agent
from .prompts import FAREWELL_AGENT_INSTRUCTION, FAREWELL_AGENT_DESCRIPTION
from .schema_and_tools import say_goodbye

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

# --- Farewell Agent ---
farewell_agent = None
try:
    farewell_agent = Agent(
        # Can use the same or a different model
        model=MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="farewell_agent",
        instruction=FAREWELL_AGENT_INSTRUCTION,
        description=FAREWELL_AGENT_DESCRIPTION,  # Crucial for delegation
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Farewell agent. Check API Key ({MODEL_GEMINI_2_0_FLASH}). Error: {e}")