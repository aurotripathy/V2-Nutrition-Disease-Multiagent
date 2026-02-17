import os
import asyncio
import warnings
import logging

# Global configuration
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

# Load environment variables
from utils.environment import load_environment
load_environment()

print("Libraries imported and environment loaded.")

# Import agent and related constants
from agent import root_agent, USER_ID_STATEFUL, SESSION_ID_STATEFUL, APP_NAME, session_service_stateful
from google.adk.runners import Runner
from google.genai.types import Content
from google.genai import types  # For creating message Content/Parts

# Define initial state data
initial_state = {
    # TODO: Add initial state data
}

# Async function to initialize session with state
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

# --- Initialize session and create Runner for this Root Agent ---
async def setup_runner():
    """Initialize session and create runner."""
    # Initialize session with state
    session_stateful = await init_session_with_state()
    print(f"✅ Session initialized with state.")
    
    # Create Runner for this Root Agent & NEW Session Service
    runner_root = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful
    )
    print(f"✅ Runner created for stateful root agent '{runner_root.agent.name}' using stateful session service.")
    return runner_root


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

    print(f"<<< Final Agent Response: {final_response_text}")


# Define the main async function for the conversation logic.
async def run_stateful_conversation():
    """Main async function that sets up runner and runs queries."""
    # Setup runner (initializes session and creates runner)
    runner_root = await setup_runner()
    
    print("\n--- Reading the query from the file 'queries.txt' ---")
    with open('query.txt', 'r') as file:
        query = file.readlines()[0]
    print(f"--- Query: {query} ---")
    
    # Loop through queries and execute them
    await query_agent_async(
        query=query,
        runner=runner_root,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL
    )

# --- Execute the `run_stateful_conversation` async function ---
# If running this code as a standard Python script from your terminal,
# the script context is synchronous. `asyncio.run()` is needed to
# create and manage an event loop to execute your async function.

if __name__ == "__main__":  # Ensures this runs only when script is executed directly
    print("Executing using 'asyncio.run()' (for standard Python scripts)...")
    try:
        # This creates an event loop, runs your async function, and closes the loop.
        asyncio.run(run_stateful_conversation())
    except Exception as e:
        print(f"An error occurred: {e}")
