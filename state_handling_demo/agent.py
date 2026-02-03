"""
Short example of capturing state in parent agent, updating it, and using the updated state in a sub-agent.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from tools import remember_name
from google.genai import types

from sub_agents.farewell_handler.agent import farewell_agent
from prompt import ROOT_AGENT_INSTRUCTION, ROOT_AGENT_DESCRIPTION

from utils.environment import load_environment
load_environment()


# Create agent with tools
root_agent = Agent(
    model="gemini-2.5-flash",
    name="greeting_orchestrator_agent",
    instruction=ROOT_AGENT_INSTRUCTION,
    description=ROOT_AGENT_DESCRIPTION,
    tools=[remember_name],
    sub_agents=[farewell_agent],
)

# Initialize services
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="greeting_farewell_app", session_service=session_service)

async def chat(user_id: str, session_id: str, message: str) -> str:
    """Send a message and get a response."""
    content = types.Content(role="user", parts=[types.Part(text=message)])
    response_text = ""
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if hasattr(event, 'content') and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text
    return response_text

async def main():
    # DEMO : Session - Remembering the user's name
    print("=" * 50)
    print("DEMO : SESSION - Remembering the user's name")
    print("=" * 50)
    
    user_id = "user_001"
    session = await session_service.create_session(app_name="greeting_farewell_app", user_id=user_id)
    
    print(f"\nUser ID: {user_id}")
    print(f"Session ID: {session.id[:8]}...")
    
    picked_name = "Alex Carp"
    print(f"\nUser: Hi! My name is {picked_name}.")
    response = await chat(user_id, session.id, f"Hi! My name is {picked_name}.")
    print(f"Agent: {response}")

    print("\nUser: Goodbye!")
    response = await chat(user_id, session.id, "Goodbye!")
    print(f"Agent: {response}")
    

if __name__ == "__main__":
    asyncio.run(main())