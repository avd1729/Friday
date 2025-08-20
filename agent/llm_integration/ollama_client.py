from agent.llm_integration.agent_client import AgentClient
import yaml
import requests

with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

base_endpoint = config["ollama"]["base_endpoint"]
chat_completion = config["ollama"]["chat_completion"]
endpoint = base_endpoint + chat_completion

model = config["ollama"]["model"]

class OllamaClient(AgentClient):
    def __init__(self):
        super().__init__()

    def generate_action(self, user_input):
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": user_input}],
            "stream": False
        }
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]

    def read_file(self, user_input, file_path):
        with open(file_path, "r") as f:
            file_content = f.read()

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that analyzes documents."},
                {"role": "user", "content": f"Here is a file:\n\n{file_content}\n\nQuestion: {user_input}"}
            ],
            "stream": False
        }
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]