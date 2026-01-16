from google.adk.agents import Agent
from .prompts import GREETING_AGENT_INSTRUCTION, GREETING_AGENT_DESCRIPTION
from .schema_and_tools import say_hello

MODEL_GEMINI_2_0_FLASH = "gemini-2.5-flash"

# --- Greeting Agent ---
greeting_agent = None
try:
    greeting_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model=MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="greeting_agent",
        instruction=GREETING_AGENT_INSTRUCTION,
        description=GREETING_AGENT_DESCRIPTION,  # Crucial for delegation
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({MODEL_GEMINI_2_0_FLASH}). Error: {e}")
