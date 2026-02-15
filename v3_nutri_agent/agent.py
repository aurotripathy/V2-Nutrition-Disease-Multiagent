"""
v3_nutri_agent - Main agent file
investigate: https://google.github.io/adk-docs/tools-custom/function-tools/#agent-tool
"""
# @title Import necessary libraries
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm  # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types  # For creating message Content/Parts

import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")

# Load environment variables
from utils.environment import load_environment
load_environment()

# Import model constants
from config import GEMINI_MODEL

print(f"Model selected: {GEMINI_MODEL}.")


session_service_stateful = InMemorySessionService()
print("✅ New InMemorySessionService created.")

SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"
APP_NAME = "v3_nutri_agent_team" 

# Define initial state data - user prefers Celsius initially
initial_state = {
    # TODO: Add initial state data
}

# Async function to initialize session with state
# deviates a bit since await cannot be called a module level code.
async def init_session_with_state():
    """Initialize session with initial state."""
    # Create the session, providing the initial state
    session_stateful = await session_service_stateful.create_session(
        app_name=APP_NAME,  # Use the consistent app name
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL,
        state=initial_state  # <<< Initialize state during creation
    )

    # Verify the initial state was set correctly
    from utils.session import verify_initial_state
    await verify_initial_state(
        session_service_stateful,
        APP_NAME,
        USER_ID_STATEFUL,
        SESSION_ID_STATEFUL
    )
    return session_stateful

# Initialize session with state (run async code)
session_stateful = asyncio.run(init_session_with_state())


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

