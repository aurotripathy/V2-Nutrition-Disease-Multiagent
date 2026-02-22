# Enhanced Search Agent

A two-agent setup using **Google ADK** (Agent Development Kit) that enhances user queries before performing web search. The root agent forwards requests to a search agent, which runs Google Search with a modified query stored in session state.

## Files

| File | Purpose |
|------|--------|
| **main.py** | Entry point: loads config, creates session/runner, and runs the agent with a user query. |
| **enhanced_search_agent.py** | Defines the root agent, search agent, and callbacks that modify and store the search query. |

---

## main.py

**Role:** Run the enhanced search agent from the command line or as a script.

- Loads `.env` and requires `GOOGLE_API_KEY`.
- Uses `InMemorySessionService` and a fixed session (`APP_NAME`, `USER_ID`, `SESSION_ID`) from the agent module.
- Creates a `Runner` with `root_agent`, then runs it asynchronously with a user message.
- Streams events and prints the final text response.

**Usage:**

```bash
# Set GOOGLE_API_KEY in .env or environment, then:
python main.py
```

By default it runs with the sample query: `"Trump's latest DHS funding"`. Change the `text` variable in `main.py` to use a different query.

**Dependencies:** `google-genai`, `google-adk`, `python-dotenv`, `asyncio`.

---

## enhanced_search_agent.py

**Role:** Define the agent graph and the logic that modifies the search query before calling Google Search.

### Agents

1. **root_agent**  
   - Model: `gemini-2.5-flash`  
   - Forwards the user’s query (with any added instructions) to the **search_agent** via `AgentTool`.  
   - Uses a **before_tool_callback** so the query can be altered and stored before the search agent runs.

2. **search_agent**  
   - Model: `gemini-2.5-flash`  
   - Instruction is **dynamic**: built by `embed_modified_query_in_search_agent_instruction` from session state.  
   - Tool: `google_search`.  
   - Effectively searches for whatever “modified query” was stored for the current session.

### Callbacks and state

- **`insert_query_plus`** (before_tool_callback)  
  - Runs before the root agent calls the search agent.  
  - Extracts the search query from the tool call (supports several shapes of `tool_name` / `args`).  
  - Builds a **modified query** by prefixing the original with `"Democratic response to "` and appending `"."`.  
  - Stores it in `SESSION_STATE[session_id]['modified_search_query']`.  
  - Returns `None` so the runner continues with the original flow (the search agent then reads from session state).

- **`embed_modified_query_in_search_agent_instruction`**  
  - Used as the **instruction** for the search agent.  
  - Reads `modified_search_query` from `SESSION_STATE` for the session.  
  - Returns an instruction of the form:  
    `"You are a specialist in Google Search. Use the google_search tool to find the following information: " + modified_query`

- **`SESSION_STATE`**  
  - Global `Dict[session_id, dict]` holding per-session data; the only key used here is `modified_search_query`.

### Flow

1. User sends a message → **root_agent** handles it.  
2. Root agent decides to call the search agent → **insert_query_plus** runs.  
3. Callback parses the query, builds `"Democratic response to <query>."`, saves it in `SESSION_STATE`.  
4. **search_agent** is invoked; its instruction is built by **embed_modified_query_in_search_agent_instruction** from that stored query.  
5. Search agent calls **google_search** with that instruction and returns results.

---

## Setup

1. Install dependencies (e.g. from project root or this folder):

   ```bash
   pip install google-genai google-adk python-dotenv
   ```

2. Create a `.env` in this directory (or parent) with:

   ```env
   GOOGLE_API_KEY=your_google_api_key
   ```

3. Run:

   ```bash
   python main.py
   ```

---

## Notes

- The “Democratic response to …” prefix is hard-coded in `insert_query_plus`; change that logic there to alter how queries are enhanced.  
- Session IDs and app/user IDs are constants in `enhanced_search_agent.py`; for multi-user or multi-session use, pass real `session_id`/`user_id` from `main.py` and ensure the callback and instruction function use them when reading/writing `SESSION_STATE`.
