from .interface.cli import driver
from .llm_integration.ollama_client import OllamaClient

def main():
    client = OllamaClient()
    driver(client)

if __name__ == "__main__":
    main()
