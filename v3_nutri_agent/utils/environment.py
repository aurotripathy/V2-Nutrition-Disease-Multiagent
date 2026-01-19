"""
Environment configuration utilities
"""
import os


def load_environment():
    """
    Load environment variables from .env file and validate required API keys.
    
    Raises:
        ValueError: If GOOGLE_API_KEY is not found in environment variables.
    """
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
