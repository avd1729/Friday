from abc import ABC, abstractmethod
from typing import List, Dict
from friday.memory.base_conversation_memory import BaseConversationMemory

class AgentClient(ABC):
    """
    Abstract base class for LLM agent clients.
    Defines the interface for agent implementations that interact with LLMs and manage conversation context.
    """
    def __init__(self, conversation_memory: BaseConversationMemory):
        self.conversation_memory = conversation_memory

    @abstractmethod
    def generate_action(user_input: str) -> dict:
        """
        Generate a structured action (e.g., JSON) from user input using the LLM.
        Args:
            user_input (str): The user's input or question.
        Returns:
            dict: Parsed action or response from the LLM.
        """
        pass
    
    @abstractmethod
    def read_file(user_input: str, file_path: str) -> None:
        """
        Analyze or process a file in the context of a user query.
        Args:
            user_input (str): The user's question about the file.
            file_path (str): Path to the file to analyze.
        Returns:
            None
        """
        pass

    @abstractmethod
    def _build_context_prompt(self, current_prompt: str) -> str:
        """
        Build a prompt for the LLM that includes relevant conversation context.
        Args:
            current_prompt (str): The current user prompt/question.
        Returns:
            str: The full prompt including context.
        """
        pass
    
    @abstractmethod
    def handle_input(self, user_input: str):
        """
        Handle user input, update context, and return a response.
        Args:
            user_input (str): The user's input or question.
        Returns:
            Any: The agent's response.
        """
        pass
    
    @abstractmethod
    def generate_natural_response(self, user_input: str):
        """
        Generate a natural language response from the LLM, given user input and context.
        Args:
            user_input (str): The user's input or question.
        Returns:
            str: The LLM's response.
        """
        pass
    
    @abstractmethod
    def generate_action(self, user_input: str, include_history: bool = False):
        """
        Generate a structured action from user input, optionally including conversation history.
        Args:
            user_input (str): The user's input or question.
            include_history (bool): Whether to include conversation history in the prompt.
        Returns:
            Any: The LLM's response or action.
        """
        pass
    
    @abstractmethod
    def get_conversation_summary(self) -> Dict:
        """
        Get a summary of the current conversation/session.
        Returns:
            Dict: Summary information (e.g., message count, last action).
        """
        pass
    
    @abstractmethod
    def clear_context(self):
        """
        Clear the conversation context/history for the current session.
        """
        pass
    
    @abstractmethod
    def get_context_messages(self, limit: int = None) -> List[Dict]:
        """
        Retrieve messages from the conversation context/history.
        Args:
            limit (int, optional): Maximum number of recent messages to return.
        Returns:
            List[Dict]: List of message dicts.
        """
        pass
    
    @abstractmethod
    def set_context_limits(self, max_messages: int = None, max_tokens_per_message: int = None):
        """
        Set limits for context size and message length.
        Args:
            max_messages (int, optional): Maximum number of messages to keep in context.
            max_tokens_per_message (int, optional): Maximum tokens per message (for truncation).
        """
        pass