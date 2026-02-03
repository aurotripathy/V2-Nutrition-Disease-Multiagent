
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext


def read_update_name_from_state(callback_context: CallbackContext) -> None:
    """Read the user's name from the state and update it."""
    state = callback_context.state
    print(f"Original user_name: {state.get('user_name', 'NOT FOUND')}")
    
    # Update the state using update method
    state.update({"user_name": "Jane Doe"})
    
    print(f"Modified State user_name: {state.get('user_name')}")
    return None

def get_user_name(tool_context: ToolContext) -> dict:
    """Get the user's name from the state."""
    state = tool_context.state
    user_name = state.get('user_name')
    print(f"User's name in tool: {user_name}")
    return {"user_name": user_name}