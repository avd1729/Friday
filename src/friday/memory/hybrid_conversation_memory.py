from friday.memory.base_conversation_memory import BaseConversationMemory

class HybridConversationMemory(BaseConversationMemory):
    def __init__(self, session_id = None, user_id = None, db_path = None):
        super().__init__(session_id, user_id, db_path)

    def add_to_history(self, role, content, metadata = None):
        return super().add_to_history(role, content, metadata)
    
    def clear(self):
        return super().clear()
    
    def get_summary(self):
        return super().get_summary()
    
    def get_messages(self, limit = None):
        return super().get_messages(limit)
    
    def set_limits(self, max_messages = None, max_tokens_per_message = None):
        return super().set_limits(max_messages, max_tokens_per_message)