from __future__ import annotations
import sqlite3
import os
from typing import Optional, List, Tuple
from datetime import datetime


DB_NAME = "browser_history.db"


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path: str = db_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)
        self._create_table()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_table(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    visited_time TEXT NOT NULL,
                    position INTEGER NOT NULL DEFAULT 0,
                    is_current INTEGER NOT NULL DEFAULT 0
                )
            """)
            conn.commit()

    def save_history(self, urls: List[str], current_url: Optional[str]) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM history")
            for idx, url in enumerate(urls):
                conn.execute(
                    "INSERT INTO history (url, visited_time, position, is_current) VALUES (?, ?, ?, ?)",
                    (url, datetime.now().isoformat(), idx, 1 if url == current_url else 0),
                )
            conn.commit()

    def load_history(self) -> Tuple[List[str], Optional[str]]:
        urls: List[str] = []
        current_url: Optional[str] = None
        with self._get_connection() as conn:
            rows = conn.execute("SELECT url, is_current FROM history ORDER BY position ASC").fetchall()
            for row in rows:
                urls.append(row["url"])
                if row["is_current"]:
                    current_url = row["url"]
        if not current_url and urls:
            current_url = urls[-1]
        return urls, current_url

    def clear_all(self) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM history")
            conn.commit()

    def get_record_count(self) -> int:
        with self._get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM history").fetchone()
            return row["cnt"] if row else 0
