from friday.memory.base_conversation_memory import BaseConversationMemory

class NoMemoryConversationMemory(BaseConversationMemory):
    """
    A memory class that does not store or return any conversation history.
    Use this if you want stateless operation.
    """
    def add_to_history(self, role, content, metadata=None):
        pass

    def get_messages(self, limit=None):
        return []

    def get_summary(self):
        return {}

    def clear(self):
        pass

    def set_limits(self, max_messages=None, max_tokens_per_message=None):
        pass
