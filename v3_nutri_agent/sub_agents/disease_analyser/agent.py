import sys
import os
from google.adk.agents import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.agent_tool import AgentTool
from .prompts import DISEASE_ANALYSER_INSTRUCTIONS, DISEASE_ANALYSER_DESCRIPTION
# Add project root to path for config import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from config import MODEL_GEMINI_2_5_FLASH

model = MODEL_GEMINI_2_5_FLASH
google_search_tool = GoogleSearchTool(bypass_multi_tools_limit=True)

disease_analyser_agent = Agent(
    name="disease_analyser",
    model=model,
    tools=[google_search_tool],
    instruction=DISEASE_ANALYSER_INSTRUCTIONS,
    description=DISEASE_ANALYSER_DESCRIPTION,
)