from __future__ import annotations
from typing import Optional, Any, List, Tuple, Callable


# ── Singly Linked List (Patient Records) ────────────────────────────────

class SLLNode:
    def __init__(self, data: dict) -> None:
        self.data: dict = data
        self.next: Optional[SLLNode] = None


class SinglyLinkedList:
    def __init__(self) -> None:
        self.head: Optional[SLLNode] = None
        self._size: int = 0

    def insert(self, data: dict) -> None:
        node = SLLNode(data)
        node.next = self.head
        self.head = node
        self._size += 1

    def insert_at_end(self, data: dict) -> None:
        node = SLLNode(data)
        if self.head is None:
            self.head = node
        else:
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = node
        self._size += 1

    def delete(self, key: str, value: Any) -> bool:
        if self.head is None:
            return False
        if self.head.data.get(key) == value:
            self.head = self.head.next
            self._size -= 1
            return True
        curr = self.head
        while curr.next:
            if curr.next.data.get(key) == value:
                curr.next = curr.next.next
                self._size -= 1
                return True
            curr = curr.next
        return False

    def update(self, key: str, value: Any, new_data: dict) -> bool:
        curr = self.head
        while curr:
            if curr.data.get(key) == value:
                new_data[key] = value
                curr.data.update(new_data)
                return True
            curr = curr.next
        return False

    def search(self, key: str, value: Any) -> Optional[dict]:
        curr = self.head
        while curr:
            if curr.data.get(key) == value:
                return curr.data
            curr = curr.next
        return None

    def search_multi(self, key: str, value: Any) -> List[dict]:
        results: List[dict] = []
        curr = self.head
        while curr:
            if value.lower() in str(curr.data.get(key, "")).lower():
                results.append(curr.data)
            curr = curr.next
        return results

    def to_list(self) -> List[dict]:
        items: List[dict] = []
        curr = self.head
        while curr:
            items.append(curr.data)
            curr = curr.next
        return items

    def rebuild(self, items: List[dict]) -> None:
        self.head = None
        self._size = 0
        for item in items:
            self.insert_at_end(item)

    @property
    def size(self) -> int:
        return self._size


# ── Doubly Linked List (Medical History) ────────────────────────────────

class DLLNode:
    def __init__(self, data: dict) -> None:
        self.data: dict = data
        self.prev: Optional[DLLNode] = None
        self.next: Optional[DLLNode] = None


class DoublyLinkedList:
    def __init__(self) -> None:
        self.head: Optional[DLLNode] = None
        self.tail: Optional[DLLNode] = None
        self.current: Optional[DLLNode] = None
        self._size: int = 0

    def insert(self, data: dict) -> None:
        node = DLLNode(data)
        if self.head is None:
            self.head = self.tail = self.current = node
        else:
            node.prev = self.tail
            if self.tail:
                self.tail.next = node
            self.tail = node
            self.current = node
        self._size += 1

    def delete(self, key: str, value: Any) -> bool:
        curr = self.head
        while curr:
            if curr.data.get(key) == value:
                if curr.prev:
                    curr.prev.next = curr.next
                else:
                    self.head = curr.next
                if curr.next:
                    curr.next.prev = curr.prev
                else:
                    self.tail = curr.prev
                if curr is self.current:
                    self.current = curr.next if curr.next else curr.prev
                self._size -= 1
                return True
            curr = curr.next
        return False

    def previous(self) -> Optional[dict]:
        if self.current and self.current.prev:
            self.current = self.current.prev
            return self.current.data
        return None

    def next_visit(self) -> Optional[dict]:
        if self.current and self.current.next:
            self.current = self.current.next
            return self.current.data
        return None

    def current_data(self) -> Optional[dict]:
        return self.current.data if self.current else None

    def to_list(self) -> List[dict]:
        items: List[dict] = []
        curr = self.head
        while curr:
            items.append(curr.data)
            curr = curr.next
        return items

    def rebuild(self, items: List[dict], current_idx: int = -1) -> None:
        self.head = self.tail = self.current = None
        self._size = 0
        for item in items:
            self.insert(item)
        if current_idx >= 0:
            idx = 0
            curr = self.head
            while curr:
                if idx == current_idx:
                    self.current = curr
                    break
                idx += 1
                curr = curr.next

    @property
    def size(self) -> int:
        return self._size

    def current_position(self) -> int:
        pos = 0
        curr = self.head
        while curr:
            if curr is self.current:
                return pos
            pos += 1
            curr = curr.next
        return -1


# ── Circular Linked List (Doctor Duty Rotation) ─────────────────────────

class CLLNode:
    def __init__(self, data: dict) -> None:
        self.data: dict = data
        self.next: Optional[CLLNode] = None


class CircularLinkedList:
    def __init__(self) -> None:
        self.head: Optional[CLLNode] = None
        self.current: Optional[CLLNode] = None
        self._size: int = 0

    def insert(self, data: dict) -> None:
        node = CLLNode(data)
        if self.head is None:
            self.head = node
            node.next = node
            self.current = node
        else:
            curr = self.head
            while curr.next is not self.head:
                curr = curr.next
            curr.next = node
            node.next = self.head
        self._size += 1

    def remove(self, key: str, value: Any) -> bool:
        if self.head is None:
            return False
        curr = self.head
        prev = None
        while True:
            if curr.data.get(key) == value:
                if curr == self.head and curr.next == self.head:
                    self.head = None
                    self.current = None
                elif curr == self.head:
                    last = self.head
                    while last.next is not self.head:
                        last = last.next
                    self.head = self.head.next
                    last.next = self.head
                    if self.current is curr:
                        self.current = self.head
                else:
                    prev.next = curr.next
                    if self.current is curr:
                        self.current = curr.next
                self._size -= 1
                return True
            prev = curr
            curr = curr.next
            if curr == self.head:
                break
        return False

    def rotate(self) -> Optional[dict]:
        if self.current is None:
            return None
        self.current = self.current.next
        return self.current.data

    def current_data(self) -> Optional[dict]:
        return self.current.data if self.current else None

    def to_list(self) -> List[dict]:
        items: List[dict] = []
        if self.head is None:
            return items
        curr = self.head
        while True:
            items.append(curr.data)
            curr = curr.next
            if curr == self.head:
                break
        return items

    def rebuild(self, items: List[dict], current_idx: int = 0) -> None:
        self.head = None
        self.current = None
        self._size = 0
        for item in items:
            self.insert(item)
        if self.head and current_idx > 0:
            idx = 0
            curr = self.head
            while idx < current_idx:
                curr = curr.next
                idx += 1
            self.current = curr

    @property
    def size(self) -> int:
        return self._size


# ── Queue (Appointment Queue) ───────────────────────────────────────────

class QueueNode:
    def __init__(self, data: dict) -> None:
        self.data: dict = data
        self.next: Optional[QueueNode] = None


class Queue:
    def __init__(self) -> None:
        self.front: Optional[QueueNode] = None
        self.rear: Optional[QueueNode] = None
        self._size: int = 0

    def enqueue(self, data: dict) -> None:
        node = QueueNode(data)
        if self.rear is None:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self._size += 1

    def dequeue(self) -> Optional[dict]:
        if self.front is None:
            return None
        data = self.front.data
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self._size -= 1
        return data

    def peek(self) -> Optional[dict]:
        return self.front.data if self.front else None

    def remove(self, key: str, value: Any) -> bool:
        if self.front is None:
            return False
        if self.front.data.get(key) == value:
            self.dequeue()
            return True
        curr = self.front
        while curr.next:
            if curr.next.data.get(key) == value:
                curr.next = curr.next.next
                if curr.next is None:
                    self.rear = curr
                self._size -= 1
                return True
            curr = curr.next
        return False

    def to_list(self) -> List[dict]:
        items: List[dict] = []
        curr = self.front
        while curr:
            items.append(curr.data)
            curr = curr.next
        return items

    def rebuild(self, items: List[dict]) -> None:
        self.front = self.rear = None
        self._size = 0
        for item in items:
            self.enqueue(item)

    @property
    def size(self) -> int:
        return self._size
