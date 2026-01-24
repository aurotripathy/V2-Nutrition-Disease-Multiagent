"""Schema and tools for the Greeting Agent."""
from typing import Optional

def say_hello(name: Optional[str] = None) -> str:
    """Provides a simple greeting. If a name is provided, it will be used.

    Args:
        name (str, optional): The name of the person to greet. Defaults to a generic greeting if not provided.

    Returns:
        str: A friendly greeting message.
    """

    capabilities = "I can give you info about the weather in a city. Please ask me about the weather in a city."
    if name:
        greeting = f"Hello, {name}! {capabilities}"
        print(f"--- Tool: say_hello called with name: {name} ---")
    else:
        greeting = f"Hello there! {capabilities}"  # Default greeting if name is None or not explicitly passed
        print(f"--- Tool: say_hello called without a specific name (name_arg_value: {name}) ---")
    return greeting
