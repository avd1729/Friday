from friday.llm_integration.agent_client import AgentClient
from friday.prompts import FILE_ANALYSIS_SYSTEM_PROMPT, GENERAL_SYSTEM_PROMPT
import importlib.resources as pkg_resources
import yaml
import requests
from friday import config
from friday.utils.parse_json import parse_json_from_model
from pathlib import Path

class OllamaClient(AgentClient):
    def __init__(self):

        self.root_dir = Path.cwd()

        with pkg_resources.files(config).joinpath("ollama_config.yml").open("r") as file:
            data = yaml.safe_load(file)

        base_endpoint = data["client"]["base_endpoint"]
        chat_completion = data["client"]["chat_completion"]

        self.endpoint = base_endpoint + chat_completion
        self.model = data["client"]["model"]

    def handle_input(self, user_input: str):

        prompt = f"{GENERAL_SYSTEM_PROMPT}\nUser query: {user_input}\nRespond ONLY with JSON."
        decision = self.generate_action(prompt)
        decision = parse_json_from_model(decision)

        action = decision.get("action")
        if action == "read_file":
            file_name = decision.get("file")
            question = decision.get("question")
            matches = list(self.root_dir.rglob(file_name))
            if not matches:
                return f"Could not find {file_name}"
            file_path = matches[0]
            return self.read_file(question, file_path)
        elif action == "generate_action":
            return self.generate_action(decision.get("question"))
        else:
            return f"Unknown action: {action}"


    def generate_action(self, user_input):
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": user_input}],
            "stream": False
        }
        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]

    def read_file(self, user_input, file_path):
        with open(file_path, "r") as f:
            file_content = f.read()

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": FILE_ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is a file:\n\n{file_content}\n\nQuestion: {user_input}"}
            ],
            "stream": False
        }
        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]