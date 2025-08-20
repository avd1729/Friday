from agent.llm_integration.agent_client import AgentClient
import yaml
import requests

with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

base_endpoint = config["ollama"]["base_endpoint"]
chat_completion = config["ollama"]["chat_completion"]
model = config["ollama"]["model"]

class OllamaClient(AgentClient):
    def __init__(self):
        super().__init__()

    def generate_action(self, user_input):
        endpoint = base_endpoint + chat_completion
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": user_input}
            ],
            "stream": False
        }

        response = requests.post(endpoint, json=payload)
        print("Status:", response.status_code)
        print("Response:", response.json())

    def read_file(file_path):
        return super().read_file()

# test = OllamaClient()
# test.generate_action("What is python?")