# State Handling Demo

Short example of capturing state in parent agent, updating it, and using the updated state in a sub-agent.

## Project Structure

```
state_handling_demo/
├── agent.py                    # Main orchestrator agent
├── prompt.py                   # Root agent instructions and description
├── tools.py                    # Root agent tools
├── session.py                  # Session management utilities
├── sub_agents/
│   └── farewell_handler/
│       ├── agent.py            # Farewell sub-agent
│       ├── prompt.py           # Farewell agent instructions
│       └── tools.py            # Farewell agent tools
└── utils/
    └── environment.py          # Environment configuration utilities
```

## Overview

This demo demonstrates:
- Capturing user state in the parent agent
- Updating state in a sub-agent callback
- Using the updated state in sub-agent responses

## Usage

Run the demo:
```bash
python agent.py
```
#### Note
Gratitude: some of the ideas came from https://arjunprabhulal.com/adk-sessions-state/