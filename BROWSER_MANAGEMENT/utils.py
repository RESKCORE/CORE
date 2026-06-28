from __future__ import annotations
import re
from typing import Optional


def validate_url(url: str) -> Optional[str]:
    url = url.strip()
    if not url:
        return None
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    pattern = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63}\.?|localhost)"
        r"(?::\d+)?"
        r"(?:/.*)?$",
        re.IGNORECASE,
    )
    if pattern.match(url):
        return url
    return None


def format_url_display(url: str, max_len: int = 50) -> str:
    if len(url) > max_len:
        return url[: max_len - 3] + "..."
    return url


def truncate(text: str, length: int = 30) -> str:
    if len(text) > length:
        return text[: length - 3] + "..."
    return text
