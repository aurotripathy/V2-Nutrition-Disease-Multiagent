import os
from dotenv import load_dotenv
import asyncio
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from enhanced_search_agent import root_agent, SESSION_STATE, APP_NAME, USER_ID, SESSION_ID


# ——————————————————————————————————————————————
# 0) Load .env from this folder
# ——————————————————————————————————————————————
try:
    load_dotenv()  # Try to load .env file from current directory or parent directories
except Exception:
    # If .env file doesn't exist or can't be read, continue without it
    # Environment variables can still be set manually
    pass

# ——————————————————————————————————————————————
# 1) Configure the Google Gen AI SDK using your .env
# ——————————————————————————————————————————————
api_key = os.getenv("GOOGLE_API_KEY")  # Retrieve the API key from environment variables
if not api_key:
    raise RuntimeError("Missing GOOGLE_API_KEY in environment variables. Please set it in your .env file or export it as an environment variable.")  # Halt if the key is not set
os.environ["GOOGLE_API_KEY"] = api_key  # Set the API key in environment (SDK reads it automatically)



# —————————————————————————————————————————————— runner "stuff" ——————————————————————————————————————————————
# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    # Initialize session state for this session
    if SESSION_ID not in SESSION_STATE:
        SESSION_STATE[SESSION_ID] = {}
        print(f"[DEBUG] Initialized session state for session_id: {SESSION_ID}")
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    print("Content Input: ", content)
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        
        
        if event.is_final_response():
            # print("Event: ", event)
            if event.content and event.content.parts:
                # Check if there's a text part
                text_parts = [part.text for part in event.content.parts if hasattr(part, 'text') and part.text]
                if text_parts:
                    final_response = text_parts[0]
                    print("Agent Response:>>>>>\n ", final_response)
                else:
                    print("Agent Response: (non-text response, possibly function call)")
            else:
                print("Agent Response: (no content available)")


text = """Trump's latest DHS funding"""

# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
# await call_agent_async(long_text)

if __name__ == "__main__":
    asyncio.run(call_agent_async(text))
    print("Done")