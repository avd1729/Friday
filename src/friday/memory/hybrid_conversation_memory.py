from friday.memory.base_conversation_memory import BaseConversationMemory
from friday.prompts import GENERAL_SYSTEM_PROMPT
from typing import List, Dict
from datetime import datetime
import os
import sqlite3
class HybridConversationMemory(BaseConversationMemory):
    def __init__(self, max_context_messages: int = 20, max_tokens_per_message: int = 2000, session_id = None, user_id = None, db_path = "db/conversation_memory.db", system_prompt: str = GENERAL_SYSTEM_PROMPT):
        self.session_start_time = datetime.now()
        self.session_id = session_id
        self.user_id = user_id
        self.db_path = db_path
        self.conversation_history: List[Dict[str, str]] = []
        self.max_context_messages = max_context_messages
        self.max_tokens_per_message = max_tokens_per_message
        self.system_prompt = system_prompt

        if system_prompt:
            self.add_to_history("system", system_prompt)

        self._init_db()
        if session_id is None:
            self.session_id = self._create_new_session(user_id)
        else:
            self.session_id = session_id

    def _connect(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True) if os.path.dirname(self.db_path) else None
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        conn = self._connect()
        cursor = conn.cursor()

        # session
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                created_at REAL
            )
            """
        )

        # messages
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                role TEXT,
                content TEXT,
                metadata TEXT,
                timestamp REAL,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            )
            """
        ) 

        conn.commit()
        conn.close()

    def _create_new_session(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO SESSIONS (user_id, created_at) VALUES (?, ?)
            """, (user_id, datetime.now().timestamp())
        )

        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return session_id
    
    def add_to_history(self, role, content, metadata = None):
        message = {
            "role": role,
            "content": self.truncate_content(content),
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            message["metadata"] = metadata
        self.conversation_history.append(message)
        self._manage_context_size()

    def truncate_content(self, content: str) -> str:
        max_chars = self.max_tokens_per_message * 4
        if len(content) > max_chars:
            return content[:max_chars] + "...[truncated]"
        return content

    def _manage_context_size(self):
        if len(self.conversation_history) > self.max_context_messages:
            system_msg = self.conversation_history[0] if self.conversation_history and self.conversation_history[0]["role"] == "system" else None
            # Calculate how many messages to remove
            num_to_remove = len(self.conversation_history) - self.max_context_messages
            # If system message exists, don't remove it
            start_idx = 1 if system_msg else 0
            # Messages to remove (excluding system message if present)
            removed = self.conversation_history[start_idx:start_idx+num_to_remove]
            # Push removed messages to DB
            if removed:
                conn = self._connect()
                cursor = conn.cursor()
                for msg in removed:
                    cursor.execute(
                        """
                        INSERT INTO messages (session_id, role, content, metadata, timestamp) VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            self.session_id,
                            msg.get("role"),
                            msg.get("content"),
                            str(msg.get("metadata")) if msg.get("metadata") else None,
                            datetime.datetime.fromisoformat(msg.get("timestamp")).timestamp() if msg.get("timestamp") else datetime.datetime.now().timestamp()
                        )
                    )
                conn.commit()
                conn.close()
            # Now trim the in-memory history
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
    
    def get_summary(self):
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
    
    def get_messages(self, limit = None):
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history.copy()
    
    def set_limits(self, max_context_messages: int = None, max_tokens_per_message: int = None):
        if max_context_messages:
            self.max_context_messages = max_context_messages
            self.manage_context_size()
        if max_tokens_per_message:
            self.max_tokens_per_message = max_tokens_per_message