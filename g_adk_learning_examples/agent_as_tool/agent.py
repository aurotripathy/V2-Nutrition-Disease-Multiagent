# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Agent-as-a-Tool: When Agent A calls Agent B as a tool (using Agent-as-a-Tool),
# Agent B's answer is passed back to Agent A, which then summarizes the answer
# and generates a response to the user.
# Agent A retains control and continues to handle future user input.


# The AgentTool class provides the following attributes for customizing its behavior:
# skip_summarization: bool: If set to True, the framework will bypass the LLM-based summarization of the tool agent's response.
# This can be useful when the tool's response is already well-formatted and requires no further processing.

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.agent_tool import AgentTool
from google.genai import types
import os

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


APP_NAME="summary_agent"
USER_ID="user1234"
SESSION_ID="1234"

summary_agent = Agent(
    model="gemini-2.5-flash",
    name="summary_agent",
    instruction="""You are an expert summarizer. Please read the following text and provide a concise summary.""",
    description="Agent to summarize text",
)

root_agent = Agent(
    model='gemini-2.0-flash',
    name='root_agent',
    instruction="""You are a helpful assistant. When the user provides a text, use the 'summarize' tool to generate a summary. Always forward the user's message exactly as received to the 'summarize' tool, without modifying or summarizing it yourself. Present the response from the tool to the user.""",
    tools=[AgentTool(agent=summary_agent, skip_summarization=False)]
)

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)


long_text = """Quantum computing represents a fundamentally different approach to computation, 
leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers 
that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively 
being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled, 
meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and 
interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such 
as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far 
faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages."""

# Note: In Colab, you can directly use 'await' at the top level.
# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
# await call_agent_async(long_text)

import asyncio
if __name__ == "__main__":  # Ensures this runs only when script is executed directly                                                                                                                                    
    print("Executing using 'asyncio.run()' (for standard Python scripts)...")
    try:
        # This creates an event loop, runs your async function, and closes the loop.                                                                                                                                     
        asyncio.run(call_agent_async(long_text))
    except Exception as e:
        print(f"An error occurred: {e}")
