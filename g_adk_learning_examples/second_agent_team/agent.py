"""
Step 4: Adding Memory and Personalization with Session State
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
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass


# Gemini API Key (Get from Google AI Studio: https://aistudio.google.com/app/apikey)
# Load from environment variable
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables. "
        "Please set it in your .env file or export it as an environment variable. "
        "Get your API key from: https://aistudio.google.com/app/apikey"
    )
os.environ["GOOGLE_API_KEY"] = api_key

print(f"Gemini API Key loaded")

# --- Define Model Constants for easier use ---
# More supported models can be referenced here: https://ai.google.dev/gemini-api/docs/models#model-variations
MODEL_GEMINI_2_5_FLASH = "gemini-2.5-flash"

print("Model configured.")


# @title 1. Initialize New Session Service and State
# Import necessary session components
from google.adk.sessions import InMemorySessionService

# Create a NEW session service instance for this state demonstration
session_service_stateful = InMemorySessionService()
print("✅ New InMemorySessionService created for state demonstration.")

# Define a NEW session ID for this part of the tutorial
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"
APP_NAME = "weather_tutorial_agent_team"  # Define APP_NAME before use

# Define initial state data - user prefers Celsius initially
initial_state = {
    "user_preference_temperature_unit": "Celsius"
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
    print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")

    # Verify the initial state was set correctly
    retrieved_session = await session_service_stateful.get_session(
        app_name=APP_NAME,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL
    )
    print("\n--- Initial Session State ---")
    if retrieved_session:
        print(retrieved_session.state)
    else:
        print("Error: Could not retrieve session.")
    return session_stateful

# Initialize session with state (run async code)
session_stateful = asyncio.run(init_session_with_state())


# @title Import tools and prompts
from schema_and_tools import get_weather_stateful
from prompts import WEATHER_AGENT_TEAM_INSTRUCTION, WEATHER_AGENT_TEAM_DESCRIPTION


# @title Define Greeting and Farewell Sub-Agents

# Import the agents from their modules
from sub_agents.greeting_agent.agent import greeting_agent
from sub_agents.farewell_agent.agent import farewell_agent


# @title Define the Root Agent with Sub-Agents

# Ensure sub-agents were created successfully before defining the root agent.
# Also ensure the  'get_weather_stateful' tool is defined.
root_agent_stateful = None
runner_root_stateful = None  # Initialize runner
from schema_and_tools import get_weather_stateful

# Check if function is defined (proper way for imported functions)
# Method 1: Use callable() - checks if it's a callable object
is_defined = callable(get_weather_stateful)
print(f"✅ State-aware 'get_weather_stateful' tool defined: {is_defined}")

if greeting_agent and farewell_agent and callable(get_weather_stateful):
    print(f"✅ Sub-agents and tools are defined. Creating stateful root agent...")
    # Let's use a capable Gemini model for the root agent to handle orchestration
    root_agent_model = MODEL_GEMINI_2_5_FLASH

    root_agent_stateful = Agent(
        name="weather_agent_v4_stateful",  # Give it a new version name
        model=root_agent_model,
        description=WEATHER_AGENT_TEAM_DESCRIPTION,
        instruction=WEATHER_AGENT_TEAM_INSTRUCTION,
        tools=[get_weather_stateful],  # Root agent still needs the weather tool for its core task
        # Key change: Link the sub-agents here!
        # insert before callback to check for quit
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report", # <<< Auto-save agent's final weather response
    )
    print(f"✅ Root Agent '{root_agent_stateful.name}' created using stateful tool and output_key.")

    # --- Create Runner for this Root Agent & NEW Session Service ---
    runner_root_stateful = Runner(
        agent=root_agent_stateful,
        app_name=APP_NAME,
        session_service=session_service_stateful # Use the NEW stateful session service
    )
    print(f"✅ Runner created for stateful root agent '{runner_root_stateful.agent.name}' using stateful session service.")

else:
    print("❌ Cannot create stateful root agent. Prerequisites missing.")
    if not greeting_agent: print(" - greeting_agent definition missing.")
    if not farewell_agent: print(" - farewell_agent definition missing.")
    if not callable(get_weather_stateful): print(" - get_weather_stateful tool missing.")


# # @title 4. Interact to Test State Flow and output_key
import asyncio  # Ensure asyncio is imported

# Ensure the stateful runner (runner_root_stateful) is available from the previous cell
# Ensure call_agent_async, USER_ID_STATEFUL, SESSION_ID_STATEFUL, APP_NAME are defined



# Ensure the call_agent_async function is defined.
async def call_agent_async(query: str, runner, user_id, session_id):
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


# Only define and run if the root agent exists
if 'runner_root_stateful' in globals() and runner_root_stateful:
    # Define the main async function for the conversation logic.
    # The 'await' keywords INSIDE this function are necessary for async operations.
    async def run_stateful_conversation():
        print("\n--- Testing State: Temperature Unit Conversion & output_key ---")
        # 1. Check weather (Uses initial state: Celsius)
        print("--- Turn 1: Requesting weather in London (expect Celsius) ---")
        await call_agent_async(query= "What's the weather in London?",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 2. Manually update state preference to Fahrenheit - DIRECTLY MODIFY STORAGE
        print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
        try:
            # Access the internal storage directly - THIS IS SPECIFIC TO InMemorySessionService for testing
            # NOTE: In production with persistent services (Database, VertexAI), you would
            # typically update state via agent actions or specific service APIs if available,
            # not by direct manipulation of internal storage.
            stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
            stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
            # Optional: You might want to update the timestamp as well if any logic depends on it
            # import time
            # stored_session.last_update_time = time.time()
            print(f"--- Stored session state updated. Current 'user_preference_temperature_unit': {stored_session.state.get('user_preference_temperature_unit', 'Not Set')} ---") # Added .get for safety
        except KeyError:
            print(f"--- Error: Could not retrieve session '{SESSION_ID_STATEFUL}' from internal storage for user '{USER_ID_STATEFUL}' in app '{APP_NAME}' to update state. Check IDs and if session was created. ---")
        except Exception as e:
             print(f"--- Error updating internal session state: {e} ---")

        # 3. Check weather again (Tool should now use Fahrenheit)
        # This will also update 'last_weather_report' via output_key
        print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
        await call_agent_async(query= "Tell me the weather in New York.",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 4. Test basic delegation (should still work)
        # This will update 'last_weather_report' again, overwriting the NY weather report
        print("\n--- Turn 3: Sending a greeting ---")
        await call_agent_async(query= "Hi!",
                               runner=runner_root_stateful,
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
