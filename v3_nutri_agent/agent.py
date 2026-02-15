"""
v3_nutri_agent - Main agent file
investigate: https://google.github.io/adk-docs/tools-custom/function-tools/#agent-tool
"""
# @title Import necessary libraries
import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm  # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types  # For creating message Content/Parts


# Import model constants
from config import GEMINI_MODEL

print(f"Model selected: {GEMINI_MODEL}.")


session_service_stateful = InMemorySessionService()
print("✅ New InMemorySessionService created.")

SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"
APP_NAME = "v3_nutri_agent_team" 



# @title Import tools and prompts
from prompts import ORCHESTRATOR_AGENT_FOR_TEAM_INSTRUCTION

# @title Define Greeting and Farewell Sub-Agents
# Import the agents from their modules
from sub_agents.greeting_handler.agent import greeting_handler_agent 
from sub_agents.farewell_handler.agent import farewell_handler_agent 
from sub_agents.ingredients_generator.agent import ingredients_generator_agent

# @title Define the Root Agent with Sub-Agents

# Ensure sub-agents were created successfully before defining the root agent.
# Also ensure the  'get_weather_stateful' tool is defined.
root_agent = None

# Check if function is defined (proper way for imported functions)
# Method 1: Use callable() - checks if it's a callable object


root_agent_model = GEMINI_MODEL

root_agent = Agent(
    name="orchestrator_agent",
    model=root_agent_model,
    description="Root orchestrator agent coordinating the sub-agents.",
    instruction=ORCHESTRATOR_AGENT_FOR_TEAM_INSTRUCTION, # Root agent still needs the weather tool for its core task
    # Key change: Link the sub-agents here!
    # insert before callback to check for quit
    sub_agents=[greeting_handler_agent, farewell_handler_agent, ingredients_generator_agent],
    output_key="TBD", # <<< Auto-save agent's final response
)
print(f"✅ Root Agent '{root_agent.name}' created using TBD.")

