from friday.llm_integration.agent_client import AgentClient
from friday.prompts import FILE_ANALYSIS_SYSTEM_PROMPT, GENERAL_SYSTEM_PROMPT, CONTEXT_PROMPT
import importlib.resources as pkg_resources
import yaml
import requests
from friday import config
from friday.utils.parse_json import parse_json_from_model
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from friday.memory.in_memory import InMemoryConversationMemory

class OllamaClient(AgentClient):
    def __init__(self, max_context_messages: int = 20, max_tokens_per_message: int = 2000):
        self.root_dir = Path.cwd()
        # Load configuration
        with pkg_resources.files(config).joinpath("ollama_config.yml").open("r") as file:
            data = yaml.safe_load(file)
        base_endpoint = data["client"]["base_endpoint"]
        chat_completion = data["client"]["chat_completion"]
        self.endpoint = base_endpoint + chat_completion
        self.model = data["client"]["model"]
        # Use InMemoryConversationMemory for context management
        self.memory = InMemoryConversationMemory(max_context_messages, max_tokens_per_message, GENERAL_SYSTEM_PROMPT)
    

    
    def _build_context_prompt(self, current_prompt: str) -> str:
        history = self.memory.get_messages()
        if not history:
            return current_prompt
        context_parts = ["Previous conversation context:"]
        for msg in history[-10:]:
            role = msg["role"].upper()
            content = msg["content"][:500]
            if "metadata" in msg and msg["metadata"].get("action"):
                content += f" [Action: {msg['metadata']['action']}]"
            context_parts.append(f"{role}: {content}")
        context_parts.append(f"\nCurrent request: {current_prompt}")
        return "\n".join(context_parts)
    
    def handle_input(self, user_input: str):
        self.memory.add_to_history("user", user_input)
        decision = self.generate_action(f"{user_input}\nRespond ONLY with JSON.", include_history=True)
        decision_parsed = parse_json_from_model(decision)
        if not decision_parsed:
            error_msg = "Failed to parse decision from model"
            self.memory.add_to_history("assistant", error_msg, {"error": "parse_failure"})
            return error_msg
        action = decision_parsed.get("action")
        response = None
        if action == "read_file":
            file_name = decision_parsed.get("file")
            question = decision_parsed.get("question")
            matches = list(self.root_dir.rglob(file_name))
            if not matches:
                response = f"Could not find {file_name}"
            else:
                file_path = matches[0]
                response = self.read_file(question, file_path)
            self.memory.add_to_history("assistant", response, {
                "action": "read_file",
                "file": file_name,
                "found": bool(matches)
            })
        elif action == "generate_action":
            question = decision_parsed.get("question")
            response = self.generate_natural_response(question)
            self.memory.add_to_history("assistant", response, {"action": "generate_action"})
        else:
            response = f"Unknown action: {action}"
            self.memory.add_to_history("assistant", response, {"error": "unknown_action"})
        return response
    
    def generate_natural_response(self, user_input: str):
        messages = []
        history = self.memory.get_messages()
        if history:
            for msg in history:
                if msg["role"] == "system":
                    messages.append({"role": "system", "content": CONTEXT_PROMPT})
                elif msg["role"] in ["user", "assistant"]:
                    if msg["content"] != user_input:
                        messages.append({"role": msg["role"], "content": msg["content"]})
        else:
            messages.append({"role": "system", "content": CONTEXT_PROMPT})
        messages.append({"role": "user", "content": user_input})
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]
    
    def generate_action(self, user_input: str, include_history: bool = False):
        messages = []
        history = self.memory.get_messages()
        if include_history and history:
            for msg in history:
                if msg["role"] in ["user", "assistant", "system"]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
        else:
            messages.append({"role": "system", "content": GENERAL_SYSTEM_PROMPT})
        messages.append({"role": "user", "content": user_input})
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]
    
    def read_file(self, user_input: str, file_path: Path):
        with open(file_path, "r") as f:
            file_content = f.read()
        context_info = ""
        history = self.memory.get_messages()
        if history:
            recent_context = [msg for msg in history[-5:] if msg["role"] == "user"]
            if recent_context:
                context_info = f"\nRecent conversation context: {recent_context[-1]['content'][:200]}"
        messages = [
            {"role": "system", "content": FILE_ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is a file:\n\n{file_content}\n\nQuestion: {user_input}{context_info}"}
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]
    
    # Context management methods
    def get_conversation_summary(self) -> Dict:
        return self.memory.get_summary()
    def clear_context(self):
        self.memory.clear()
    def get_context_messages(self, limit: int = None) -> List[Dict]:
        return self.memory.get_messages(limit)
    def set_context_limits(self, max_messages: int = None, max_tokens_per_message: int = None):
        self.memory.set_limits(max_messages, max_tokens_per_message)