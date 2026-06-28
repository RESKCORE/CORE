from __future__ import annotations
from typing import Optional, List, Tuple
from linked_list import BrowserHistory
from database import DatabaseManager


class BrowserApp:
    def __init__(self) -> None:
        self.history = BrowserHistory()
        self.db = DatabaseManager()
        self._load_from_database()

    # ── Visit ───────────────────────────────────────────────────────────

    def visit(self, url: str) -> bool:
        url = url.strip()
        if not url:
            return False
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        current_url = self.history.show_current()
        if current_url == url:
            return False
        self.history.insert(url)
        self._save_to_database()
        return True

    # ── Navigation ──────────────────────────────────────────────────────

    def back(self) -> Optional[str]:
        node = self.history.back()
        if node:
            self._save_to_database()
            return node.url
        return None

    def forward(self) -> Optional[str]:
        node = self.history.forward()
        if node:
            self._save_to_database()
            return node.url
        return None

    # ── Current ─────────────────────────────────────────────────────────

    def show_current(self) -> Optional[str]:
        return self.history.show_current()

    # ── History ─────────────────────────────────────────────────────────

    def show_history(self) -> List[Tuple[str, bool]]:
        return self.history.show_history()

    # ── Search ──────────────────────────────────────────────────────────

    def search(self, query: str) -> List[Tuple[int, str, bool]]:
        return self.history.search(query)

    # ── Delete ──────────────────────────────────────────────────────────

    def delete_page(self, url: str) -> bool:
        result = self.history.delete_page(url)
        if result:
            self._save_to_database()
        return result

    # ── Clear History ───────────────────────────────────────────────────

    def clear_history(self) -> None:
        self.history.clear_history()
        self.db.clear_all()

    # ── Delete Forward History ──────────────────────────────────────────

    def delete_forward_history(self) -> None:
        self.history.delete_forward_history()
        self._save_to_database()

    # ── Properties ──────────────────────────────────────────────────────

    @property
    def total_count(self) -> int:
        return self.history.size

    def get_position(self) -> int:
        return self.history.get_position()

    def can_go_back(self) -> bool:
        return not self.history.is_at_oldest()

    def can_go_forward(self) -> bool:
        return not self.history.is_at_newest()

    def get_db_record_count(self) -> int:
        return self.db.get_record_count()

    # ── Database persistence ────────────────────────────────────────────

    def _save_to_database(self) -> None:
        urls = self.history.to_list()
        current_url = self.history.show_current()
        self.db.save_history(urls, current_url)

    def _load_from_database(self) -> None:
        urls, current_url = self.db.load_history()
        if urls:
            self.history.rebuild_from_urls(urls, current_url)

    def sync_database(self) -> None:
        self._save_to_database()
