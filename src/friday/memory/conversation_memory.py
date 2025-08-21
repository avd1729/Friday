from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class ConversationMemory(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None):
        pass

    @abstractmethod
    def add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None):
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
    def get_messages(self, limit: int = None) -> List[Dict]:
        pass

    @abstractmethod
    def set_limits(self, max_messages: int = None, max_tokens_per_message: int = None):
        pass
