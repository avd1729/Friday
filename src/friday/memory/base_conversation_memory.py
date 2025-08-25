from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseConversationMemory(ABC):
    """
    Abstract base class for conversation memory backends.
    Provides an interface for storing and retrieving conversation history, supporting both in-memory and persistent (e.g., database) implementations.

    Attributes:
        session_id (Optional[str]): Identifier for the conversation session (useful for persistent storage).
        user_id (Optional[str]): Identifier for the user (useful for multi-user systems).
    """
    def __init__(self, session_id: Optional[str] = None, user_id: Optional[str] = None):
        self.session_id = session_id
        self.user_id = user_id

    @abstractmethod
    def add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a message to the conversation history.
        Args:
            role (str): The role of the message sender (e.g., 'user', 'assistant', 'system').
            content (str): The message content.
            metadata (Optional[Dict]): Optional metadata for the message (e.g., action, file info).
        """
        pass


    @abstractmethod
    def clear(self):
        """
        Clear the conversation history for the current session/user.
        """
        pass


    @abstractmethod
    def get_summary(self) -> Dict:
        """
        Get a summary of the conversation (e.g., message count, session duration, last action).
        Returns:
            Dict: Summary information about the conversation.
        """
        pass


    @abstractmethod
    def get_messages(self, limit: int = None) -> List[Dict]:
        """
        Retrieve messages from the conversation history.
        Args:
            limit (int, optional): Maximum number of recent messages to return.
        Returns:
            List[Dict]: List of message dicts.
        """
        pass


    @abstractmethod
    def set_limits(self, max_messages: int = None, max_tokens_per_message: int = None):
        """
        Set limits for context size and message length.
        Args:
            max_messages (int, optional): Maximum number of messages to keep in history.
            max_tokens_per_message (int, optional): Maximum tokens per message (for truncation).
        """
        pass
