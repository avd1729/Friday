from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseConversationMemory(ABC):
    def __init__(self, session_id: Optional[str] = None, user_id: Optional[str] = None):
        self.session_id = session_id
        self.user_id = user_id
    @abstractmethod
    def add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None):
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
