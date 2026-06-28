"""
models.py
----------
Defines the core data model used across the Browser History Manager.

This module contains the `Node` class, which represents a single visited
webpage entry inside the Doubly Linked List. Each Node stores the URL,
the time it was visited, and pointers to the previous and next nodes.

Author: Reddy Santosh Kumar
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Node:
    """
    Represents a single node in the Doubly Linked List.

    Each Node corresponds to one visited webpage and holds:
    - The URL of the page.
    - The timestamp when the page was visited.
    - A reference to the previous node (`prev`) in history.
    - A reference to the next node (`next`) in history.

    Attributes:
        url (str): The website URL stored in this node.
        visited_time (str): ISO formatted timestamp of when the page was visited.
        prev (Optional[Node]): Pointer to the previous node (older page).
        next (Optional[Node]): Pointer to the next node (newer page).
        db_id (Optional[int]): The primary key of this node's row in SQLite,
            used to keep the in-memory linked list synced with the database.
    """

    url: str
    visited_time: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    prev: Optional["Node"] = field(default=None, repr=False, compare=False)
    next: Optional["Node"] = field(default=None, repr=False, compare=False)
    db_id: Optional[int] = None

    def __repr__(self) -> str:
        """Return a readable representation of the node (used for debugging)."""
        return f"Node(url={self.url!r}, visited_time={self.visited_time!r})"
