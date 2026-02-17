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
from prompts import ORCHESTRATOR_AGENT_FOR_TEAM_DESCRIPTION
# @title Define Greeting and Farewell Sub-Agents
# Import the agents from their modules
from sub_agents.greeting_handler.agent import greeting_handler_agent 
from sub_agents.farewell_handler.agent import farewell_handler_agent 
from sub_agents.ingredients_generator.agent import ingredients_generator_agent

# Import callback types
from google.adk.agents.callback_context import CallbackContext
from google.genai.types import Content
from typing import Optional


def before_agent_callback_root_agent(callback_context: CallbackContext) -> Optional[Content]:
    """Callback to log which sub-agent is being invoked."""
    print(f"[Bf🤖CB] [ROOT] Before_agent_callback triggered for agent: {callback_context.agent_name}")
    
    # Check if this is a sub-agent invocation
    # The agent_name will show which agent is being invoked
    sub_agent_names = [
        greeting_handler_agent.name,
        farewell_handler_agent.name,
        ingredients_generator_agent.name
    ]
    
    if callback_context.agent_name in sub_agent_names:
        print(f"[Bf🤖CB] [ROOT] ➡️ Sub-agent invoked: {callback_context.agent_name}")
    elif callback_context.agent_name == "orchestrator_agent":
        print(f"[Bf🤖CB] [ROOT] ➡️ Root orchestrator agent invoked")
    else:
        print(f"[Bf🤖CB] [ROOT] ➡️ Agent invoked: {callback_context.agent_name}")
    
    # Optional: Log the initial user input if available
    if callback_context.user_content:
        print(f"[Bf🤖CB] [ROOT] Initial User Input: {callback_context.user_content.parts[0].text}")
    
    # Returning None allows the agent execution to proceed normally
    return None

root_agent_model = GEMINI_MODEL

root_agent = Agent(
    name="orchestrator_agent",
    model=root_agent_model,
    description=ORCHESTRATOR_AGENT_FOR_TEAM_DESCRIPTION,
    instruction=ORCHESTRATOR_AGENT_FOR_TEAM_INSTRUCTION,
    sub_agents=[greeting_handler_agent, farewell_handler_agent, ingredients_generator_agent],
    before_agent_callback=[before_agent_callback_root_agent],
    output_key="TBD", # <<< Auto-save agent's final response
)
print(f"✅ Root Agent '{root_agent.name}' created using TBD.")

