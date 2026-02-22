# enhance_search

Module that provides an enhanced search agent: it modifies user queries (e.g. prefixes with "Democratic response to ...") and stores the modified query in session state so the search agent uses it.

## Exports

- `root_agent` – Top-level agent that forwards to the search agent
- `search_agent` – Agent that runs Google search using the modified query from session state
- `SESSION_STATE` – Dict used to store modified query per session
- `APP_NAME`, `USER_ID`, `SESSION_ID` – Constants for session/runner setup

## Usage

```python
from enhance_search import root_agent, SESSION_STATE, APP_NAME, USER_ID, SESSION_ID
```
