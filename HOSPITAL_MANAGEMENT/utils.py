from __future__ import annotations
import re
import csv
import io
from typing import Optional, List
from datetime import datetime


def generate_id(prefix: str, existing_ids: list) -> str:
    max_num = 0
    for eid in existing_ids:
        match = re.search(rf"{prefix}(\d+)", eid)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    return f"{prefix}{max_num + 1:04d}"


def validate_contact(contact: str) -> bool:
    return bool(re.match(r"^\d{10}$", contact))


def validate_age(age: str) -> bool:
    try:
        a = int(age)
        return 0 <= a <= 150
    except ValueError:
        return False


def format_date(dt_str: Optional[str]) -> str:
    if not dt_str:
        return ""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d-%b-%Y %I:%M %p")
    except (ValueError, TypeError):
        return dt_str


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def truncate(text: str, length: int = 30) -> str:
    text = str(text)
    if len(text) > length:
        return text[: length - 3] + "..."
    return text


def to_csv(data: List[dict], filename: str = "export.csv") -> str:
    output = io.StringIO()
    if not data:
        return ""
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def to_markdown_table(data: List[dict]) -> str:
    if not data:
        return ""
    headers = list(data[0].keys())
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in data:
        lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
    return "\n".join(lines)
