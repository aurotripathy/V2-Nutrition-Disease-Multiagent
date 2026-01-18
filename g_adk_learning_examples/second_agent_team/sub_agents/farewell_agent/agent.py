from google.adk.agents import Agent
from .prompts import FAREWELL_AGENT_INSTRUCTION, FAREWELL_AGENT_DESCRIPTION
from .schema_and_tools import say_goodbye

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"


# --- Redefine Farewell Agent (from Step 3) ---
farewell_agent = None
try:
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent",
        instruction=FAREWELL_AGENT_INSTRUCTION,
        description=FAREWELL_AGENT_DESCRIPTION,
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Error: {e}")
