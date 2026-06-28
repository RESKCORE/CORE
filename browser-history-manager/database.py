"""
database.py
------------
Handles all SQLite persistence for the Browser History Manager.

The DatabaseManager class is solely responsible for talking to SQLite.
It NEVER acts as the primary data structure -- the Doubly Linked List
in `linked_list.py` is the in-memory source of truth while the app is
running. SQLite only mirrors that state so history survives between
runs of the Streamlit app.

Database file: browser_history.db
Table: history (id, url, visited_time, position, is_current)

Author: Reddy Santosh Kumar
"""

import sqlite3
from typing import List, Tuple

DB_FILE_NAME = "browser_history.db"


class DatabaseManager:
    """
    Manages all SQLite operations for persisting browser history.

    Attributes:
        db_path (str): Filesystem path to the SQLite database file.
    """

    def __init__(self, db_path: str = DB_FILE_NAME) -> None:
        """
        Initialize the DatabaseManager and ensure the `history` table
        exists (creating the database file automatically if needed).

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self._create_table()

    # ------------------------------------------------------------------
    # CONNECTION HELPERS
    # ------------------------------------------------------------------

    def _get_connection(self) -> sqlite3.Connection:
        """
        Create and return a new SQLite connection.

        Returns:
            sqlite3.Connection: An open connection to the database file.

        Raises:
            sqlite3.Error: If the connection cannot be established.
        """
        # check_same_thread=False allows safe use from Streamlit's
        # single-threaded rerun model without connection errors.
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _create_table(self) -> None:
        """
        Create the `history` table if it does not already exist.

        Columns:
            id (INTEGER PRIMARY KEY AUTOINCREMENT)
            url (TEXT NOT NULL)
            visited_time (TEXT NOT NULL)
            position (INTEGER NOT NULL) -- order of the node in the list
            is_current (INTEGER NOT NULL) -- 1 if this was the current node, else 0

        Raises:
            sqlite3.Error: If table creation fails.
        """
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        visited_time TEXT NOT NULL,
                        position INTEGER NOT NULL,
                        is_current INTEGER NOT NULL DEFAULT 0
                    )
                    """
                )
                conn.commit()
        except sqlite3.Error as error:
            # Re-raise with a clearer message; the caller (BrowserApp)
            # is responsible for surfacing this to the Streamlit UI.
            raise sqlite3.Error(f"Failed to create 'history' table: {error}") from error

    # ------------------------------------------------------------------
    # WRITE OPERATIONS
    # ------------------------------------------------------------------

    def clear_table(self) -> None:
        """
        Delete every row from the `history` table.

        Raises:
            sqlite3.Error: If the delete operation fails.
        """
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM history")
                conn.commit()
        except sqlite3.Error as error:
            raise sqlite3.Error(f"Failed to clear history table: {error}") from error

    def save_all(self, rows: List[Tuple[str, str, int, int]]) -> None:
        """
        Overwrite the entire `history` table with a fresh snapshot of
        the in-memory linked list. This is the main "sync" operation
        called after every mutating action (visit, back, forward,
        delete, clear).

        Args:
            rows (List[Tuple[str, str, int, int]]): A list of tuples in
                the form (url, visited_time, position, is_current),
                ordered from head to tail.

        Raises:
            sqlite3.Error: If the write transaction fails.
        """
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM history")
                conn.executemany(
                    """
                    INSERT INTO history (url, visited_time, position, is_current)
                    VALUES (?, ?, ?, ?)
                    """,
                    rows,
                )
                conn.commit()
        except sqlite3.Error as error:
            raise sqlite3.Error(f"Failed to save history to database: {error}") from error

    # ------------------------------------------------------------------
    # READ OPERATIONS
    # ------------------------------------------------------------------

    def load_all(self) -> List[Tuple[int, str, str, int, int]]:
        """
        Load every row from the `history` table, ordered by `position`
        ascending (oldest visit first), ready for linked-list
        reconstruction.

        Returns:
            List[Tuple[int, str, str, int, int]]: Rows in the form
            (id, url, visited_time, position, is_current).

        Raises:
            sqlite3.Error: If the read operation fails.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT id, url, visited_time, position, is_current
                    FROM history
                    ORDER BY position ASC
                    """
                )
                return cursor.fetchall()
        except sqlite3.Error as error:
            raise sqlite3.Error(f"Failed to load history from database: {error}") from error

    def get_row_count(self) -> int:
        """
        Return the total number of rows currently stored in the
        `history` table. Useful for displaying "Database Status" in
        the Streamlit sidebar.

        Returns:
            int: Number of rows in the `history` table.

        Raises:
            sqlite3.Error: If the count query fails.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM history")
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as error:
            raise sqlite3.Error(f"Failed to count history rows: {error}") from error

    def is_connected(self) -> bool:
        """
        Quick health-check used by the UI's "Database Status" indicator.

        Returns:
            bool: True if a connection can be opened and a trivial
            query executes successfully, False otherwise.
        """
        try:
            with self._get_connection() as conn:
                conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False
