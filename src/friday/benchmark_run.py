from friday.llm_integration.ollama_client import OllamaClient
from friday.memory.in_memory_conversation_memory import InMemoryConversationMemory
from friday.memory.sqlite_conversation_memory import SqliteConversationMemory
from friday.utils.benchmark import benchmark_function, compare_benchmarks

def run_agent_with_memory(memory_backend, prompt: str):
    client = OllamaClient(memory=memory_backend)
    return client.handle_input(prompt)

if __name__ == "__main__":
    prompt = "What is the best roadmap to learn Rust?"
    in_memory = InMemoryConversationMemory()
    sqlite_memory = SqliteConversationMemory()

    results = {}
    results['Ollama + InMemory'] = benchmark_function(run_agent_with_memory, in_memory, prompt, repeat=3)
    results['Ollama + SQLite'] = benchmark_function(run_agent_with_memory, sqlite_memory, prompt, repeat=3)

    compare_benchmarks(results)

# Benchmark Results:
# Ollama + InMemory: avg=63.2780s min=36.1707s max=77.4606s
# Ollama + SQLite: avg=44.6977s min=36.9160s max=51.6509s