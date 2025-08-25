from friday.memory.base_conversation_memory import BaseConversationMemory
import sqlite3
from datetime import time
class SqliteConversationMemory(BaseConversationMemory):
    def __init__(self, session_id = None, user_id = None, db_path="conversation_memory.db"):
        self.session_id = session_id
        self.user_id = user_id
        self.db_path = db_path

        if session_id is None:
            self.session_id = self._create_new_session(user_id)
        else:
            self.session_id = session_id

    def _connect(self):
        return sqlite3.connect(self)
    
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
            """, (user_id, time.time)
        )

        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return session_id
    
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