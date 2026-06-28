"""
linked_list.py
---------------
Implements the core Doubly Linked List data structure that powers the
Browser History Manager.

This is the heart of the project. Every browser navigation action
(visit, back, forward, delete, search) is implemented as a pure
Doubly Linked List operation. No Python list is used as the primary
storage mechanism -- SQLite is used only for persistence (saving and
reloading state between runs).

Classes:
    BrowserHistory: Manages a doubly linked list of visited Node objects
                     and exposes browser-like navigation operations.

Author: Reddy Santosh Kumar
"""

from typing import List, Optional

from models import Node


class BrowserHistory:
    """
    Implements browser history navigation using a Doubly Linked List.

    The list is structured as:

        head <-> node1 <-> node2 <-> ... <-> tail

    The `current` pointer always points to the page that is presently
    "open" in the browser, similar to how a real browser tracks the
    active tab's position in its history stack.

    Attributes:
        head (Optional[Node]): The first (oldest) node in the history.
        tail (Optional[Node]): The last (newest) node in the history.
        current (Optional[Node]): The node representing the currently
            displayed page.
        size (int): Number of nodes currently in the list.
    """

    def __init__(self) -> None:
        """Initialize an empty browser history (no nodes)."""
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self.current: Optional[Node] = None
        self.size: int = 0

    # ------------------------------------------------------------------
    # CORE LINKED LIST OPERATIONS
    # ------------------------------------------------------------------

    def visit(self, url: str, visited_time: Optional[str] = None) -> Node:
        """
        Visit a new URL.

        Behaviour (matches real browsers):
        - If the user is somewhere in the middle of history and visits a
          new URL, ALL forward history (every node after `current`) is
          permanently deleted before the new node is appended. This is
          exactly how Chrome/Edge behave: navigating to a brand-new page
          erases the "forward" stack.
        - The new node is appended after the current node and becomes
          the new `current` and `tail`.

        Args:
            url (str): The website URL being visited.
            visited_time (Optional[str]): Optional explicit timestamp
                (used when reconstructing history from the database).
                If None, the current time is used.

        Returns:
            Node: The newly created and inserted node.

        Time Complexity: O(1) amortized when visiting from the tail,
            O(k) when forward history of size k must first be discarded.
        Space Complexity: O(1) additional space for the new node.
        """
        # If we are not at the tail, discard forward history first.
        if self.current is not None and self.current.next is not None:
            self.delete_forward_history()

        new_node = Node(url=url) if visited_time is None else Node(url=url, visited_time=visited_time)

        if self.head is None:
            # Empty list: new node becomes head, tail, and current.
            self.head = new_node
            self.tail = new_node
            self.current = new_node
        else:
            # Append after current node (which, after the forward-history
            # cleanup above, is guaranteed to be the tail).
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
            self.current = new_node

        self.size += 1
        return new_node

    def back(self) -> Optional[Node]:
        """
        Move the current pointer one step backward (toward `head`).

        Returns:
            Optional[Node]: The node now pointed to by `current`, or
            None if there is no previous page (already at the oldest page,
            or history is empty).

        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        if self.current is None or self.current.prev is None:
            # Null navigation: nothing to go back to.
            return None
        self.current = self.current.prev
        return self.current

    def forward(self) -> Optional[Node]:
        """
        Move the current pointer one step forward (toward `tail`).

        Returns:
            Optional[Node]: The node now pointed to by `current`, or
            None if there is no next page (already at the newest page,
            or history is empty).

        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        if self.current is None or self.current.next is None:
            # Null navigation: nothing to go forward to.
            return None
        self.current = self.current.next
        return self.current

    def show_current(self) -> Optional[Node]:
        """
        Return the node currently being viewed.

        Returns:
            Optional[Node]: The current node, or None if history is empty.

        Time Complexity: O(1)
        """
        return self.current

    def show_history(self) -> List[Node]:
        """
        Traverse the entire list from head to tail and return all nodes
        in chronological order (oldest -> newest).

        Returns:
            List[Node]: All nodes in the history, in visit order.

        Time Complexity: O(n), where n is the number of nodes.
        Space Complexity: O(n) for the returned list of references.
        """
        nodes = []
        cursor = self.head
        while cursor is not None:
            nodes.append(cursor)
            cursor = cursor.next
        return nodes

    def search(self, keyword: str) -> List[Node]:
        """
        Search the linked list for nodes whose URL contains the given
        keyword (case-insensitive substring search).

        Args:
            keyword (str): The text to search for within stored URLs.

        Returns:
            List[Node]: All matching nodes, in chronological order.

        Time Complexity: O(n), since every node must be visited once.
        Space Complexity: O(k), where k is the number of matches.
        """
        if not keyword:
            return []
        keyword_lower = keyword.lower()
        matches = []
        cursor = self.head
        while cursor is not None:
            if keyword_lower in cursor.url.lower():
                matches.append(cursor)
            cursor = cursor.next
        return matches

    def delete_page(self, target: Node) -> bool:
        """
        Delete a specific node from the linked list, re-linking its
        neighbours so the list remains intact.

        Handles all edge cases:
        - Deleting the head.
        - Deleting the tail.
        - Deleting the current node (current shifts to `prev`, or
          `next` if there is no previous node, or None if the list
          becomes empty).
        - Deleting the only node in the list.

        Args:
            target (Node): The node to remove.

        Returns:
            bool: True if deletion succeeded, False if the node was
            not found in the list.

        Time Complexity: O(1), since we already hold a direct reference
            to the node (no traversal needed to locate it).
        Space Complexity: O(1)
        """
        if target is None:
            return False

        prev_node = target.prev
        next_node = target.next

        # Re-link the previous node's `next` pointer.
        if prev_node is not None:
            prev_node.next = next_node
        else:
            # Target was the head.
            self.head = next_node

        # Re-link the next node's `prev` pointer.
        if next_node is not None:
            next_node.prev = prev_node
        else:
            # Target was the tail.
            self.tail = prev_node

        # If we just deleted the current node, move current sensibly.
        if self.current is target:
            self.current = prev_node if prev_node is not None else next_node

        # Detach target fully (helps garbage collection, avoids dangling refs).
        target.prev = None
        target.next = None

        self.size -= 1
        return True

    def delete_forward_history(self) -> int:
        """
        Delete every node AFTER the current node (the "forward" stack).

        This mirrors real browser behaviour: once you navigate to a new
        URL while sitting in the middle of history, every page that was
        ahead of you becomes unreachable and is discarded.

        Returns:
            int: The number of nodes that were deleted.

        Time Complexity: O(k), where k is the number of forward nodes
            being removed.
        Space Complexity: O(1)
        """
        if self.current is None:
            return 0

        cursor = self.current.next
        deleted_count = 0
        while cursor is not None:
            next_cursor = cursor.next
            cursor.prev = None
            cursor.next = None
            deleted_count += 1
            cursor = next_cursor

        self.current.next = None
        self.tail = self.current
        self.size -= deleted_count
        return deleted_count

    def clear_history(self) -> None:
        """
        Remove all nodes from the linked list, resetting it to an empty
        state. Equivalent to clicking "Clear browsing data" in a real
        browser.

        Time Complexity: O(1), since Python's garbage collector reclaims
            the detached chain of nodes once references are dropped;
            no explicit per-node traversal is required.
        Space Complexity: O(1)
        """
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0

    def __len__(self) -> int:
        """Return the number of nodes currently in the history."""
        return self.size
