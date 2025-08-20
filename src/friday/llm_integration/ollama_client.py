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
        
        # Context management
        self.conversation_history: List[Dict[str, str]] = []
        self.max_context_messages = max_context_messages
        self.max_tokens_per_message = max_tokens_per_message
        self.session_start_time = datetime.now()
        
        # Add system prompt to history once at initialization
        self._add_to_history("system", GENERAL_SYSTEM_PROMPT)
    
    def _add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None):
        message = {
            "role": role,
            "content": self._truncate_content(content),
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            message["metadata"] = metadata
            
        self.conversation_history.append(message)
        self._manage_context_size()
    
    def _truncate_content(self, content: str) -> str:
        # Rough estimation: 1 token ≈ 4 characters
        max_chars = self.max_tokens_per_message * 4
        if len(content) > max_chars:
            return content[:max_chars] + "...[truncated]"
        return content
    
    def _manage_context_size(self):
        if len(self.conversation_history) > self.max_context_messages:
            # Always keep the system prompt (first message) and recent messages
            system_msg = self.conversation_history[0] if self.conversation_history[0]["role"] == "system" else None
            recent_messages = self.conversation_history[-(self.max_context_messages-1):]
            
            if system_msg:
                self.conversation_history = [system_msg] + recent_messages
            else:
                self.conversation_history = self.conversation_history[-self.max_context_messages:]
    
    def _build_context_prompt(self, current_prompt: str) -> str:
        if not self.conversation_history:
            return current_prompt
        
        context_parts = ["Previous conversation context:"]
        
        # Add recent relevant messages
        for msg in self.conversation_history[-10:]:  # Last 10 messages for context
            role = msg["role"].upper()
            content = msg["content"][:500]  # Truncate for context
            if "metadata" in msg and msg["metadata"].get("action"):
                content += f" [Action: {msg['metadata']['action']}]"
            context_parts.append(f"{role}: {content}")
        
        context_parts.append(f"\nCurrent request: {current_prompt}")
        return "\n".join(context_parts)
    
    def handle_input(self, user_input: str):
        # Add user input to history
        self._add_to_history("user", user_input)
        
        decision = self.generate_action(f"{user_input}\nRespond ONLY with JSON.", include_history=True)
        decision_parsed = parse_json_from_model(decision)
        
        if not decision_parsed:
            error_msg = "Failed to parse decision from model"
            self._add_to_history("assistant", error_msg, {"error": "parse_failure"})
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
            
            self._add_to_history("assistant", response, {
                "action": "read_file", 
                "file": file_name,
                "found": bool(matches)
            })
            
        elif action == "generate_action":
            question = decision_parsed.get("question")
            # Generate the actual response to the user's question (without JSON instruction)
            response = self.generate_natural_response(question)
            self._add_to_history("assistant", response, {"action": "generate_action"})
            
        else:
            response = f"Unknown action: {action}"
            self._add_to_history("assistant", response, {"error": "unknown_action"})
        
        return response
    
    def generate_natural_response(self, user_input: str):
        messages = []
        
        # Build messages with conversation context but exclude JSON instruction from system prompt
        if self.conversation_history:
            for msg in self.conversation_history:
                if msg["role"] == "system":
                    # Use a natural conversation system prompt instead of JSON-only prompt
                    messages.append({
                        "role": "system", 
                        "content": CONTEXT_PROMPT
                    })
                elif msg["role"] in ["user", "assistant"]:
                    # Skip the current user input (will be added separately)
                    if msg["content"] != user_input:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
        else:
            messages.append({
                "role": "system", 
                "content": CONTEXT_PROMPT
            })
        
        # Add the current question
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
        
        if include_history and self.conversation_history:
            for msg in self.conversation_history:
                if msg["role"] in ["user", "assistant", "system"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
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
        
        # Build context-aware file analysis prompt
        context_info = ""
        if self.conversation_history:
            recent_context = [msg for msg in self.conversation_history[-5:] 
                            if msg["role"] == "user"]
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
        return {
            "total_messages": len(self.conversation_history),
            "session_duration": str(datetime.now() - self.session_start_time),
            "unique_files_accessed": len(set(
                msg.get("metadata", {}).get("file", "") 
                for msg in self.conversation_history 
                if msg.get("metadata", {}).get("action") == "read_file"
            )) if any(msg.get("metadata", {}).get("file") for msg in self.conversation_history) else 0,
            "last_action": self.conversation_history[-1].get("metadata", {}).get("action", "none") if self.conversation_history else "none"
        }
    
    def clear_context(self):
        self.conversation_history.clear()
        self.session_start_time = datetime.now()
        # Re-add system prompt
        self._add_to_history("system", GENERAL_SYSTEM_PROMPT)
    
    def get_context_messages(self, limit: int = None) -> List[Dict]:
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history.copy()
    
    def set_context_limits(self, max_messages: int = None, max_tokens_per_message: int = None):
        if max_messages:
            self.max_context_messages = max_messages
            self._manage_context_size()
        if max_tokens_per_message:
            self.max_tokens_per_message = max_tokens_per_message