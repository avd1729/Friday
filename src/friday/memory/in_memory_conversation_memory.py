
from typing import List, Dict, Optional
from datetime import datetime
from .base_conversation_memory import BaseConversationMemory
from friday.prompts import GENERAL_SYSTEM_PROMPT

class InMemoryConversationMemory(BaseConversationMemory):
    def __init__(self, max_context_messages: int = 20, max_tokens_per_message: int = 2000, system_prompt: str = GENERAL_SYSTEM_PROMPT):
        self.conversation_history: List[Dict[str, str]] = []
        self.max_context_messages = max_context_messages
        self.max_tokens_per_message = max_tokens_per_message
        self.session_start_time = datetime.now()
        self.system_prompt = system_prompt
        if system_prompt:
            self.add_to_history("system", system_prompt)

    def add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None):
        message = {
            "role": role,
            "content": self.truncate_content(content),
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            message["metadata"] = metadata
        self.conversation_history.append(message)
        self.manage_context_size()

    def truncate_content(self, content: str) -> str:
        max_chars = self.max_tokens_per_message * 4
        if len(content) > max_chars:
            return content[:max_chars] + "...[truncated]"
        return content

    def manage_context_size(self):
        if len(self.conversation_history) > self.max_context_messages:
            system_msg = self.conversation_history[0] if self.conversation_history and self.conversation_history[0]["role"] == "system" else None
            recent_messages = self.conversation_history[-(self.max_context_messages-1):]
            if system_msg:
                self.conversation_history = [system_msg] + recent_messages
            else:
                self.conversation_history = self.conversation_history[-self.max_context_messages:]

    def clear(self):
        self.conversation_history.clear()
        self.session_start_time = datetime.now()
        if self.system_prompt:
            self.add_to_history("system", self.system_prompt)

    def get_summary(self) -> Dict:
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

    def get_messages(self, limit: int = None) -> List[Dict]:
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history.copy()

    def set_limits(self, max_context_messages: int = None, max_tokens_per_message: int = None):
        if max_context_messages:
            self.max_context_messages = max_context_messages
            self.manage_context_size()
        if max_tokens_per_message:
            self.max_tokens_per_message = max_tokens_per_message
