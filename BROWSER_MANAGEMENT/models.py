from __future__ import annotations
from typing import Optional, Any


class Node:
    def __init__(self, url: str) -> None:
        self.url: str = url
        self.prev: Optional[Node] = None
        self.next: Optional[Node] = None
