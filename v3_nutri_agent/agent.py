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

# --- Create Runner for this Root Agent & NEW Session Service ---
runner_root = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service_stateful # Use the NEW stateful session service
)
print(f"✅ Runner created for stateful root agent '{runner_root.agent.name}' using stateful session service.")


# # @title 4. Interact to Test State Flow and output_key
import asyncio  # Ensure asyncio is imported


# Ensure the call_agent_async function is defined.
async def query_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # You can uncomment the line below to see *all* events during execution
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:  # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            # Add more checks here if needed (e.g., specific error codes)
            break  # Stop processing events once the final response is found

    print(f"<<< Agent Response: {final_response_text}")


# Ok, here's where we send a series of queries to the agent and see how it responds.
# Only define and run if the root agent exists
if 'runner_root' in globals() and runner_root:
    # Define the main async function for the conversation logic.
    # The 'await' keywords INSIDE this function are necessary for async operations.
    async def run_stateful_conversation():
        print("\n--- Querying State: ---")
        
        # Read queries from queries.txt file
        queries_file = os.path.join(os.path.dirname(__file__), 'queries.txt')
        queries = []
        try:
            with open(queries_file, 'r') as f:
                for line in f:
                    query = line.strip()
                    if query:  # Skip empty lines
                        queries.append(query)
            print(f"✅ Loaded {len(queries)} queries from queries.txt")
        except FileNotFoundError:
            print(f"⚠️ Warning: queries.txt not found. Using empty query list.")
        except Exception as e:
            print(f"⚠️ Error reading queries.txt: {e}")
        
        # Loop through queries and execute them
        for i, query in enumerate(queries, 1):
            print(f"\n--- Query {i}/{len(queries)}: {query[:50]}... ---" if len(query) > 50 else f"\n--- Query {i}/{len(queries)}: {query} ---")
            await query_agent_async(
                query=query,
                runner=runner_root,
                user_id=USER_ID_STATEFUL,
                session_id=SESSION_ID_STATEFUL
            )

    # --- Execute the `run_stateful_conversation` async function ---

    # METHOD 2: asyncio.run (For Standard Python Scripts [.py])
    # If running this code as a standard Python script from your terminal,
    # the script context is synchronous. `asyncio.run()` is needed to
    # create and manage an event loop to execute your async function.

    import asyncio
    if __name__ == "__main__":  # Ensures this runs only when script is executed directly
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # This creates an event loop, runs your async function, and closes the loop.
            asyncio.run(run_stateful_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")


else:
    # This message prints if the root agent variable wasn't found earlier
    print("\n⚠️ Skipping agent team conversation execution as the root agent was not successfully defined in a previous step.")
