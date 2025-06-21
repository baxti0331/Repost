import sqlite3
from typing import List, Dict

class Database:
    def __init__(self, db_path='botdata.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                channels TEXT NOT NULL, -- JSON строка с ID каналов
                schedule_time TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_channels (
                user_id INTEGER NOT NULL,
                channel_id TEXT NOT NULL,
                title TEXT NOT NULL,
                PRIMARY KEY (user_id, channel_id)
            )
        ''')
        self.conn.commit()

    def get_due_posts(self) -> List[Dict]:
        import json
        from datetime import datetime

        cursor = self.conn.cursor()
        now_iso = datetime.utcnow().isoformat()
        cursor.execute("SELECT id, user_id, message, channels, schedule_time FROM scheduled_posts WHERE schedule_time <= ?", (now_iso,))
        rows = cursor.fetchall()

        posts = []
        for row in rows:
            posts.append({
                "id": row[0],
                "user_id": row[1],
                "message": row[2],
                "channels": json.loads(row[3]),
                "schedule_time": row[4],
            })
        return posts

    def remove_scheduled_post(self, post_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM scheduled_posts WHERE id = ?", (post_id,))
        self.conn.commit()

    def get_user_channels(self, user_id: int) -> Dict[str, Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT channel_id, title FROM user_channels WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        return {channel_id: {"title": title} for channel_id, title in rows}

    # Пример методов для добавления и удаления каналов, постов можно добавить по необходимости
