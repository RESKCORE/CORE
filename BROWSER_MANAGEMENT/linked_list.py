from __future__ import annotations
from typing import Optional, List, Tuple
from models import Node


class BrowserHistory:
    def __init__(self) -> None:
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self.current: Optional[Node] = None
        self._size: int = 0

    # ── Insert ──────────────────────────────────────────────────────────

    def insert(self, url: str) -> Node:
        node = Node(url)
        if self.head is None:
            self.head = self.tail = self.current = node
        else:
            node.prev = self.current
            if self.current is not None:
                if self.current.next is not None:
                    self._remove_forward_history(self.current)
                self.current.next = node
            self.tail = node
            self.current = node
        self._size += 1
        return node

    def _remove_forward_history(self, from_node: Node) -> None:
        curr = from_node.next
        while curr:
            nxt = curr.next
            curr.prev = None
            curr.next = None
            self._size -= 1
            curr = nxt
        from_node.next = None
        self.tail = from_node

    # ── Navigation ──────────────────────────────────────────────────────

    def back(self) -> Optional[Node]:
        if self.current is None or self.current.prev is None:
            return None
        self.current = self.current.prev
        return self.current

    def forward(self) -> Optional[Node]:
        if self.current is None or self.current.next is None:
            return None
        self.current = self.current.next
        return self.current

    # ── Current ─────────────────────────────────────────────────────────

    def show_current(self) -> Optional[str]:
        return self.current.url if self.current else None

    # ── Traversal ───────────────────────────────────────────────────────

    def show_history(self) -> List[Tuple[str, bool]]:
        result: List[Tuple[str, bool]] = []
        curr = self.head
        while curr:
            result.append((curr.url, curr is self.current))
            curr = curr.next
        return result

    def to_list(self) -> List[str]:
        urls: List[str] = []
        curr = self.head
        while curr:
            urls.append(curr.url)
            curr = curr.next
        return urls

    # ── Search ──────────────────────────────────────────────────────────

    def search(self, query: str) -> List[Tuple[int, str, bool]]:
        results: List[Tuple[int, str, bool]] = []
        idx = 0
        curr = self.head
        while curr:
            if query.lower() in curr.url.lower():
                results.append((idx, curr.url, curr is self.current))
            idx += 1
            curr = curr.next
        return results

    # ── Delete ──────────────────────────────────────────────────────────

    def delete_page(self, url: str) -> bool:
        if self.head is None:
            return False
        curr = self.head
        while curr and curr.url != url:
            curr = curr.next
        if curr is None:
            return False
        was_current = curr is self.current

        if curr.prev:
            curr.prev.next = curr.next
        else:
            self.head = curr.next

        if curr.next:
            curr.next.prev = curr.prev
        else:
            self.tail = curr.prev

        if was_current:
            self.current = curr.next if curr.next else curr.prev

        self._size -= 1
        return True

    # ── Clear ───────────────────────────────────────────────────────────

    def clear_history(self) -> None:
        curr = self.head
        while curr:
            nxt = curr.next
            curr.prev = None
            curr.next = None
            curr = nxt
        self.head = self.tail = self.current = None
        self._size = 0

    # ── Delete Forward History ──────────────────────────────────────────

    def delete_forward_history(self) -> None:
        if self.current is None:
            return
        self._remove_forward_history(self.current)

    # ── Rebuild ─────────────────────────────────────────────────────────

    def rebuild_from_urls(self, urls: List[str], current_url: Optional[str] = None) -> None:
        self.clear_history()
        for url in urls:
            self.insert(url)
            if current_url is not None and url == current_url:
                pass
        if current_url:
            curr = self.head
            while curr:
                if curr.url == current_url:
                    self.current = curr
                    break
                curr = curr.next

    # ── Properties ──────────────────────────────────────────────────────

    @property
    def size(self) -> int:
        return self._size

    def get_position(self) -> int:
        pos = 0
        curr = self.head
        while curr and curr is not self.current:
            pos += 1
            curr = curr.next
        return pos if self.current else 0

    def is_at_oldest(self) -> bool:
        return self.current is None or self.current.prev is None

    def is_at_newest(self) -> bool:
        return self.current is None or self.current.next is None
