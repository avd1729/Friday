# Memory Backends in Friday

Friday supports multiple memory backends for conversation history management. Each backend is suitable for different use cases and scales. Below is an overview of each backend and its characteristics.

## 1. InMemoryConversationMemory

- **Location:** `src/friday/memory/in_memory_conversation_memory.py`
- **Description:** Stores the entire conversation history in memory (RAM) for the duration of the process. Fast and simple, but history is lost when the process ends.
- **Features:**
	- Keeps a configurable number of recent messages and tokens.
	- Supports a system prompt as the first message.
	- Good for short-lived or stateless sessions.
- **Best for:** Testing, development, or single-session use.

## 2. SqliteConversationMemory

- **Location:** `src/friday/memory/sqlite_conversation_memory.py`
- **Description:** Persists conversation history in a SQLite database file. Supports multiple sessions and users.
- **Features:**
	- Stores all messages in a database table, with session and user support.
	- Persists history across process restarts.
	- Supports summary statistics (total messages, session duration, unique files accessed, last action).
- **Best for:** Production, multi-session, or when persistence is required.

## 3. HybridConversationMemory

- **Location:** `src/friday/memory/hybrid_conversation_memory.py`
- **Description:** Combines in-memory speed for recent messages with SQLite persistence for older messages. Recent messages are kept in memory; older ones are pushed to the database.
- **Features:**
	- Fast access to recent context, persistent storage for older context.
	- Configurable limits for in-memory messages and tokens.
	- Suitable for long-running sessions with large histories.
- **Best for:** Scenarios needing both speed and persistence, or when context size may exceed memory limits.

## 4. NoMemoryConversationMemory

- **Location:** `src/friday/memory/no_memory_conversation_memory.py`
- **Description:** Stateless backend that does not store or return any conversation history. All methods are no-ops or return empty results.
- **Features:**
	- No memory usage or persistence.
	- Useful for stateless or one-off interactions.
- **Best for:** Stateless API calls, privacy-sensitive use cases, or when memory is not needed.

---

**How to use:**

When initializing the `OllamaClient`, pass the desired memory backend:

```python
from friday.llm_integration.ollama_client import OllamaClient
from friday.memory.in_memory_conversation_memory import InMemoryConversationMemory

client = OllamaClient(memory=InMemoryConversationMemory())
```

Replace `InMemoryConversationMemory` with any of the above classes as needed.
