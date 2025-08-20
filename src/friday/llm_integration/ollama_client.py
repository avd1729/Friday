from friday.llm_integration.agent_client import AgentClient
from friday.prompts import FILE_ANALYSIS_SYSTEM_PROMPT
import importlib.resources as pkg_resources
import yaml
import requests
from friday import config
import re
from pathlib import Path

with pkg_resources.files(config).joinpath("ollama_config.yml").open("r") as file:
    data = yaml.safe_load(file)

base_endpoint = data["client"]["base_endpoint"]
chat_completion = data["client"]["chat_completion"]
endpoint = base_endpoint + chat_completion

model = data["client"]["model"]

class OllamaClient(AgentClient):
    def __init__(self):
        super().__init__()
        self.root_dir = Path.cwd()

    def handle_input(self, user_input: str) -> str:
        # detect file mentions like "cli.py", "parser.py", "settings.json"
        file_mentions = re.findall(r'\b[\w-]+\.\w+\b', user_input)

        if file_mentions:
            responses = []
            for filename in file_mentions:
                matches = list(self.root_dir.rglob(filename))  # search recursively

                if not matches:
                    responses.append(f"Could not find {filename} in project.")
                    continue

                if len(matches) > 1:
                    responses.append(
                        f"Multiple matches for {filename}: {', '.join(str(m) for m in matches)}"
                    )
                    continue

                file_path = matches[0]
                question = user_input.replace(filename, "").strip()
                responses.append(self.read_file(question, file_path))
            return "\n\n".join(responses)

        # no file mentioned → general question
        return self.generate_action(user_input)

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
                {"role": "system", "content": FILE_ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is a file:\n\n{file_content}\n\nQuestion: {user_input}"}
            ],
            "stream": False
        }
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]