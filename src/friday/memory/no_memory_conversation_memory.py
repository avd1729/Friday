from friday.memory.base_conversation_memory import BaseConversationMemory
from friday.prompts import GENERAL_SYSTEM_PROMPT

class NoMemoryConversationMemory(BaseConversationMemory):
    """
    A memory class that does not store or return any conversation history except the system prompt.
    Use this if you want stateless operation.
    """
    def __init__(self, system_prompt: str = GENERAL_SYSTEM_PROMPT):
        self.system_prompt = system_prompt

    def add_to_history(self, role, content, metadata=None):
        pass  # No-op

    def get_messages(self, limit=None):
        # Always return just the system prompt as the first message
        if self.system_prompt:
            return [{"role": "system", "content": self.system_prompt}]
        return []

    def get_summary(self):
        return {"total_messages": 1 if self.system_prompt else 0, "system_prompt": bool(self.system_prompt)}

    def clear(self):
        pass  # No-op

    def set_limits(self, max_messages=None, max_tokens_per_message=None):
        pass  # No-op
