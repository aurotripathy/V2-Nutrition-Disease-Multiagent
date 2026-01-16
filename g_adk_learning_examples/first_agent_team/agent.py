"""
step 3 of https://google.github.io/adk-docs/tutorials/agent-team/
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

print(f"Gemini API Key loaded: {api_key}")

# --- Define Model Constants for easier use ---

# More supported models can be referenced here: https://ai.google.dev/gemini-api/docs/models#model-variations
MODEL_GEMINI_2_0_FLASH = "gemini-2.5-flash"

print("\nEnvironment configured.")


# @title Import tools and prompts
from schema_and_tools import get_weather
from prompts import WEATHER_AGENT_TEAM_INSTRUCTION, WEATHER_AGENT_TEAM_DESCRIPTION

# Example tool usage (optional test)
print(get_weather("New York"))
print(get_weather("Paris"))


# @title Define Greeting and Farewell Sub-Agents

# Import the agents from their modules
from sub_agents.greeting_agent.agent import greeting_agent
from sub_agents.farewell_agent.agent import farewell_agent


# @title Define the Root Agent with Sub-Agents

# Ensure sub-agents were created successfully before defining the root agent.
# Also ensure the original 'get_weather' tool is defined.
root_agent = None
runner_root = None  # Initialize runner

if greeting_agent and farewell_agent:
    # Let's use a capable Gemini model for the root agent to handle orchestration
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    weather_agent_team = Agent(
        name="weather_agent_v2",  # Give it a new version name
        model=root_agent_model,
        description=WEATHER_AGENT_TEAM_DESCRIPTION,
        instruction=WEATHER_AGENT_TEAM_INSTRUCTION,
        tools=[get_weather],  # Root agent still needs the weather tool for its core task
        # Key change: Link the sub-agents here!
        # insert before callback to check for quit
        sub_agents=[greeting_agent, farewell_agent]
    )
    print(f"✅ Root Agent '{weather_agent_team.name}' created using model '{root_agent_model}' with sub-agents: {[sa.name for sa in weather_agent_team.sub_agents]}")

else:
    print("❌ Cannot create root agent because one or more sub-agents failed to initialize.")
    if not greeting_agent:
        print(" - Greeting Agent is missing.")
    if not farewell_agent:
        print(" - Farewell Agent is missing.")


# @title Interact with the Agent Team
import asyncio  # Ensure asyncio is imported

# Ensure the root agent (e.g., 'weather_agent_team' or 'root_agent' from the previous cell) is defined.


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


async def async_input(prompt: str = "") -> str:
    """Reads a line of input asynchronously."""
    # Run the blocking input() function in a separate thread
    return await asyncio.to_thread(input, prompt)

# Check if the root agent variable exists before defining the conversation function
root_agent_var_name = 'root_agent'  # Default name from Step 3 guide
if 'weather_agent_team' in globals():  # Check if user used this name instead
    root_agent_var_name = 'weather_agent_team'
elif 'root_agent' not in globals():
    print("⚠️ Root agent ('root_agent' or 'weather_agent_team') not found. Cannot define run_team_conversation.")
    # Assign a dummy value to prevent NameError later if the code block runs anyway
    root_agent = None  # Or set a flag to prevent execution

# Only define and run if the root agent exists
if root_agent_var_name in globals() and globals()[root_agent_var_name]:
    # Define the main async function for the conversation logic.
    # The 'await' keywords INSIDE this function are necessary for async operations.
    async def run_team_conversation():
        print("\n--- Testing Agent Team Delegation ---")
        session_service = InMemorySessionService()
        APP_NAME = "weather_tutorial_agent_team"
        USER_ID = "user_1_agent_team"
        SESSION_ID = "session_001_agent_team"
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

        actual_root_agent = globals()[root_agent_var_name]
        runner_agent_team = Runner(  # Or use InMemoryRunner
            agent=actual_root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runner created for agent '{actual_root_agent.name}'.")

        # --- Interactions using await (correct within async def) ---
        await call_agent_async(query="Hello there, Teddy",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)

        while True:

            try:
                # Await user input asynchronously
                user_input = await async_input("Enter a city name or 'quit': ")

                await call_agent_async(query=f"{user_input}",
                                       runner=runner_agent_team,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting due to interrupt...")
                break

    # --- Execute the `run_team_conversation` async function ---

    # METHOD 2: asyncio.run (For Standard Python Scripts [.py])
    # If running this code as a standard Python script from your terminal,
    # the script context is synchronous. `asyncio.run()` is needed to
    # create and manage an event loop to execute your async function.

    import asyncio
    if __name__ == "__main__":  # Ensures this runs only when script is executed directly
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # This creates an event loop, runs your async function, and closes the loop.
            asyncio.run(run_team_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")


else:
    # This message prints if the root agent variable wasn't found earlier
    print("\n⚠️ Skipping agent team conversation execution as the root agent was not successfully defined in a previous step.")
