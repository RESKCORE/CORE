"""
browser.py
-----------
Defines the `BrowserApp` class, which acts as the controller layer
connecting the in-memory `BrowserHistory` (Doubly Linked List) with
the `DatabaseManager` (SQLite persistence).

This module contains NO Streamlit code. It is pure business logic,
making it independently testable and reusable. `app.py` is responsible
only for rendering the UI and calling into this layer.

Author: Reddy Santosh Kumar
"""

from typing import List, Optional, Tuple

from database import DatabaseManager
from linked_list import BrowserHistory
from models import Node
from utils import is_valid_url, normalize_url


class DuplicateVisitError(Exception):
    """Raised when the user tries to visit the same URL as the current page."""


class EmptyHistoryError(Exception):
    """Raised when an operation requires history but none exists."""


class InvalidURLError(Exception):
    """Raised when a URL fails validation."""


class BrowserApp:
    """
    High-level controller that ties together the Doubly Linked List
    (`BrowserHistory`) and the SQLite persistence layer
    (`DatabaseManager`).

    Every public method here represents one user-facing action
    (visit, back, forward, search, delete, clear) and automatically
    keeps SQLite in sync with the in-memory list after each mutation.

    Attributes:
        history (BrowserHistory): The in-memory doubly linked list.
        db (DatabaseManager): The SQLite persistence manager.
    """

    def __init__(self, db_path: str = "browser_history.db") -> None:
        """
        Initialize the BrowserApp, set up the database connection, and
        load any previously saved history from SQLite into a fresh
        in-memory linked list.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db = DatabaseManager(db_path)
        self.history = BrowserHistory()
        self.load_from_database()

    # ------------------------------------------------------------------
    # CORE BROWSER ACTIONS
    # ------------------------------------------------------------------

    def visit(self, url: str) -> Node:
        """
        Visit a new website URL.

        Validates the URL, prevents accidental duplicate visits to the
        exact page that is already current, performs the linked-list
        insertion (which also clears forward history if applicable),
        and finally persists the updated state to SQLite.

        Args:
            url (str): The raw URL entered by the user.

        Returns:
            Node: The newly created node representing the visited page.

        Raises:
            InvalidURLError: If the URL fails validation.
            DuplicateVisitError: If the URL matches the current page exactly.
        """
        if not is_valid_url(url):
            raise InvalidURLError(f"'{url}' is not a valid URL.")

        normalized = normalize_url(url)

        current_node = self.history.show_current()
        if current_node is not None and current_node.url == normalized:
            raise DuplicateVisitError(
                f"'{normalized}' is already the current page."
            )

        new_node = self.history.visit(normalized)
        self.sync_database()
        return new_node

    def back(self) -> Optional[Node]:
        """
        Navigate one step backward in history.

        Returns:
            Optional[Node]: The node now being viewed, or None if there
            was nowhere to go back to.

        Raises:
            EmptyHistoryError: If there is no history at all.
        """
        if self.history.size == 0:
            raise EmptyHistoryError("Cannot go back: history is empty.")
        result = self.history.back()
        self.sync_database()
        return result

    def forward(self) -> Optional[Node]:
        """
        Navigate one step forward in history.

        Returns:
            Optional[Node]: The node now being viewed, or None if there
            was nowhere to go forward to.

        Raises:
            EmptyHistoryError: If there is no history at all.
        """
        if self.history.size == 0:
            raise EmptyHistoryError("Cannot go forward: history is empty.")
        result = self.history.forward()
        self.sync_database()
        return result

    def show_current(self) -> Optional[Node]:
        """
        Get the currently active page.

        Returns:
            Optional[Node]: The current node, or None if history is empty.
        """
        return self.history.show_current()

    def show_history(self) -> List[Node]:
        """
        Get the full browsing history in chronological order.

        Returns:
            List[Node]: All nodes from oldest to newest.
        """
        return self.history.show_history()

    def search(self, keyword: str) -> List[Node]:
        """
        Search the browsing history for URLs matching a keyword.

        Args:
            keyword (str): The search term.

        Returns:
            List[Node]: Matching nodes, in chronological order.
        """
        return self.history.search(keyword)

    def delete_page(self, target: Node) -> bool:
        """
        Delete a specific page from the history.

        Args:
            target (Node): The node to delete.

        Returns:
            bool: True if the deletion succeeded.

        Raises:
            EmptyHistoryError: If history is already empty.
        """
        if self.history.size == 0:
            raise EmptyHistoryError("Cannot delete: history is empty.")
        result = self.history.delete_page(target)
        self.sync_database()
        return result

    def delete_forward_history(self) -> int:
        """
        Delete all forward history ahead of the current page.

        Returns:
            int: Number of nodes removed.
        """
        removed = self.history.delete_forward_history()
        self.sync_database()
        return removed

    def clear_history(self) -> None:
        """
        Clear all browsing history, both in memory and in SQLite.
        """
        self.history.clear_history()
        self.db.clear_table()

    # ------------------------------------------------------------------
    # DATABASE SYNC OPERATIONS
    # ------------------------------------------------------------------

    def load_from_database(self) -> None:
        """
        Load saved history rows from SQLite (ordered by position) and
        reconstruct the in-memory doubly linked list, restoring the
        `current` pointer to whichever node was marked `is_current`.

        This is called once automatically when BrowserApp starts up,
        fulfilling the requirement that the app "continues from the
        last current node" after a restart.

        Raises:
            sqlite3.Error: Propagated if the database read fails.
        """
        rows = self.db.load_all()
        if not rows:
            return

        current_position: Optional[int] = None

        for db_id, url, visited_time, position, is_current in rows:
            node = self.history.visit(url, visited_time=visited_time)
            node.db_id = db_id
            if is_current:
                current_position = position

        # Restore the current pointer to the correct node by position.
        if current_position is not None:
            cursor = self.history.head
            index = 0
            while cursor is not None:
                if index == current_position:
                    self.history.current = cursor
                    break
                cursor = cursor.next
                index += 1

    def save_to_database(self) -> None:
        """
        Persist the entire in-memory linked list to SQLite in one
        atomic transaction, overwriting whatever was previously stored.

        Raises:
            sqlite3.Error: Propagated if the database write fails.
        """
        rows: List[Tuple[str, str, int, int]] = []
        nodes = self.history.show_history()
        for position, node in enumerate(nodes):
            is_current = 1 if node is self.history.current else 0
            rows.append((node.url, node.visited_time, position, is_current))
        self.db.save_all(rows)

    def sync_database(self) -> None:
        """
        Convenience wrapper that re-saves the full linked list state
        to SQLite. Called after every mutating action so the database
        never drifts out of sync with the in-memory list.

        Raises:
            sqlite3.Error: Propagated if the underlying save fails.
        """
        self.save_to_database()

    # ------------------------------------------------------------------
    # STATUS HELPERS (used by the Streamlit sidebar)
    # ------------------------------------------------------------------

    def get_total_count(self) -> int:
        """
        Get the total number of pages currently in history.

        Returns:
            int: Number of nodes in the linked list.
        """
        return self.history.size

    def get_db_row_count(self) -> int:
        """
        Get the number of rows currently persisted in SQLite.

        Returns:
            int: Row count in the `history` table.
        """
        return self.db.get_row_count()

    def is_database_connected(self) -> bool:
        """
        Check whether the SQLite database is reachable.

        Returns:
            bool: True if the database connection is healthy.
        """
        return self.db.is_connected()

    def can_go_back(self) -> bool:
        """
        Check whether a `back()` navigation is currently possible.

        Returns:
            bool: True if there is a previous page to navigate to.
        """
        current = self.history.show_current()
        return current is not None and current.prev is not None

    def can_go_forward(self) -> bool:
        """
        Check whether a `forward()` navigation is currently possible.

        Returns:
            bool: True if there is a next page to navigate to.
        """
        current = self.history.show_current()
        return current is not None and current.next is not None
