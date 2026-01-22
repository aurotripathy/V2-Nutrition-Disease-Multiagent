# v3_nutri_agent

Google ADK Multi-Agent Nutrition Application

## Architecture

```
                    ┌─────────────────────────┐
                    │  orchestrator_agent     │
                    │    (Root Agent)         │
                    └───────────┬─────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
    │ greetings_handler│  │ farewell_handler │  │ ingredients_generator│
    │    (Sub-Agent)   │  │   (Sub-Agent)    │  │    (Sub-Agent)       │
    └──────────────────┘  └──────────────────┘  └──────────┬───────────┘
                                                            │
                                                            │ (agent-as-tool)
                                                            ▼
                                                    ┌──────────────────┐
                                                    │ disease_analyzer │
                                                    │  (Agent-as-Tool) │
                                                    └──────────────────┘
```

### Components

- **orchestrator_agent**: Root agent that coordinates all sub-agents
- **greetings_handler**: Handles greeting interactions
- **farewell_handler**: Handles farewell interactions  
- **ingredients_generator**: Generates ingredients list
- **disease_analyzer**: Called as a tool by ingredients_generator
