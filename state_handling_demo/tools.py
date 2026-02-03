from google.adk.tools import ToolContext

def remember_name(name: str, tool_context: ToolContext) -> dict:
    """Remember the user's name."""
    state = tool_context.state
    state["user_name"] = name
    print(f"Name {name} remembered")
    return 