from friday.memory.base_conversation_memory import BaseConversationMemory
import sqlite3
import json
import os
from datetime import datetime
class SqliteConversationMemory(BaseConversationMemory):
    def __init__(self, session_id=None, user_id=None, db_path="db/conversation_memory.db", system_prompt: str = None):
        self.session_start_time = datetime.now()
        self.session_id = session_id
        self.user_id = user_id
        self.db_path = db_path
        self.system_prompt = system_prompt

        self._init_db()
        if session_id is None:
            self.session_id = self._create_new_session(user_id)
        else:
            self.session_id = session_id

        # Ensure system prompt is present as the first message if provided and not already present
        if self.system_prompt:
            messages = self.get_messages(limit=1)
            if not messages or messages[0]["role"] != "system":
                self.add_to_history("system", self.system_prompt)

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
            """, (user_id, datetime.now())
        )

        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return session_id
    
    def add_to_history(self, role, content, metadata=None):
        # Only allow one system prompt at the start
        if role == "system":
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM messages WHERE session_id = ? AND role = 'system'",
                (self.session_id,)
            )
            if cursor.fetchone()[0] > 0:
                conn.close()
                return
            conn.close()
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO MESSAGES (session_id, role, content, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (self.session_id, role, content, json.dumps(metadata) if metadata else None, datetime.now().timestamp())
        )
        conn.commit()
        conn.close()
    
    def clear(self):
        pass
    
    def get_summary(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM MESSAGES WHERE session_id = ?", (self.session_id,) 
        )
        total_messages = cursor.fetchone()[0]

        cursor.execute(
            "SELECT created_at FROM sessions WHERE session_id = ?", (self.session_id,)
        )
        row = cursor.fetchone()
        session_start_time = datetime.fromtimestamp(row[0]) if row else datetime.now()
        session_duration = str(datetime.now() - session_start_time)

        # Unique files accessed
        cursor.execute("""
            SELECT metadata FROM messages 
            WHERE session_id = ?
        """, (self.session_id,))
        file_set = set()
        for (meta_str,) in cursor.fetchall():
            if meta_str:
                try:
                    metadata = json.loads(meta_str)
                    if metadata.get("action") == "read_file":
                        file_set.add(metadata.get("file", ""))
                except:
                    pass
        unique_files_accessed = len(file_set)

        cursor.execute("""
            SELECT metadata FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        """, (self.session_id,))
        last_meta = cursor.fetchone()
        if last_meta and last_meta[0]:
            try:
                last_action = json.loads(last_meta[0]).get("action", "none")
            except:
                last_action = "none"
        else:
            last_action = "none"

        conn.close()

        return {
            "total_messages": total_messages,
            "session_duration": session_duration,
            "unique_files_accessed": unique_files_accessed,
            "last_action": last_action
        }
    
    def get_messages(self, limit=None):
        conn = self._connect()
        cursor = conn.cursor()
        query = """
            SELECT role, content, metadata, timestamp 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        """
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query, (self.session_id,))
        rows = cursor.fetchall()
        conn.close()
        messages = []
        for role, content, metadata, timestamp in rows:
            msg = {
                "role": role,
                "content": content,
                "timestamp": datetime.fromtimestamp(timestamp).isoformat()
            }
            if metadata:
                try:
                    msg["metadata"] = json.loads(metadata)
                except:
                    msg["metadata"] = {}
            messages.append(msg)
        # Ensure system prompt is always the first message if set
        if self.system_prompt:
            if not messages or messages[0]["role"] != "system":
                messages = [{"role": "system", "content": self.system_prompt, "timestamp": self.session_start_time.isoformat()}] + messages
        return messages

    
    def set_limits(self, max_messages = None, max_tokens_per_message = None):
        return super().set_limits(max_messages, max_tokens_per_message)