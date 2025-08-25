from .interface.cli import driver
from .llm_integration.ollama_client import OllamaClient
from .memory.in_memory_conversation_memory import InMemoryConversationMemory

def main():
    client = OllamaClient(memory=InMemoryConversationMemory())
    driver(client)

if __name__ == "__main__":
    main()
