from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class ConversationMemory(ABC):
    def __init__(self, max_context_messages: int, max_tokens_per_message: int, system_prompt: str):
        self.max_context_messages = max_context_messages
        self.max_tokens_per_message = max_tokens_per_message
        self.system_prompt = system_prompt

    @abstractmethod
    def add_to_history(self, role: str, content: str, metadata: Optional[Dict]):
        pass


    @abstractmethod
    def truncate_content(self, content: str) -> str:
        pass

    @abstractmethod
    def manage_context_size(self):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def get_summary(self) -> Dict:
        pass

    @abstractmethod
    def get_messages(self, limit: int) -> List[Dict]:
        pass

    @abstractmethod
    def set_limits(self, max_messages: int, max_tokens_per_message: int):
        pass
