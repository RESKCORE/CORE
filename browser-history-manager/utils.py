"""
utils.py
---------
Small reusable helper functions used across the Browser History Manager.

Keeping these here (rather than scattering ad-hoc logic inside app.py
or browser.py) follows the DRY principle and keeps each module focused
on a single responsibility.

Author: Reddy Santosh Kumar
"""

import re
from datetime import datetime

# A reasonably permissive regex for validating typical website URLs and
# bare domain names (e.g. "google.com", "https://github.com/user/repo").
_URL_PATTERN = re.compile(
    r"^(https?://)?"                      # optional scheme
    r"([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}"      # domain.tld (one or more labels)
    r"(:\d+)?"                             # optional port
    r"(/[^\s]*)?$"                         # optional path/query/fragment
)


def is_valid_url(url: str) -> bool:
    """
    Validate whether a given string looks like a usable website URL.

    Accepts URLs with or without a scheme (e.g. both "google.com" and
    "https://google.com" are valid), as long as they contain at least
    one dot-separated domain label followed by a valid TLD.

    Args:
        url (str): The URL string to validate.

    Returns:
        bool: True if the string appears to be a valid URL, False otherwise.
    """
    if not url or not url.strip():
        return False
    return bool(_URL_PATTERN.match(url.strip()))


def normalize_url(url: str) -> str:
    """
    Normalize a URL by trimming whitespace and adding a default
    "https://" scheme if none is present. This keeps stored URLs
    consistent for display and comparison.

    Args:
        url (str): The raw URL string entered by the user.

    Returns:
        str: The normalized URL.
    """
    cleaned = url.strip()
    if not cleaned.lower().startswith(("http://", "https://")):
        cleaned = f"https://{cleaned}"
    return cleaned


def format_timestamp(iso_timestamp: str) -> str:
    """
    Convert an ISO 8601 timestamp string into a friendly, human-readable
    format for display in the Streamlit UI (e.g. "28 Jun 2026, 02:15 PM").

    Args:
        iso_timestamp (str): An ISO formatted timestamp string.

    Returns:
        str: A human-readable formatted timestamp. If parsing fails,
        the original string is returned unchanged.
    """
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime("%d %b %Y, %I:%M %p")
    except (ValueError, TypeError):
        return iso_timestamp


def extract_display_name(url: str) -> str:
    """
    Extract a short, friendly display name from a URL for use in
    the linked-list visualization (e.g. "https://www.google.com/search"
    becomes "google").

    Args:
        url (str): The full URL.

    Returns:
        str: A short display-friendly name derived from the URL's domain.
    """
    cleaned = url.strip()
    cleaned = re.sub(r"^https?://", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^www\.", "", cleaned, flags=re.IGNORECASE)
    # Take only the domain portion (before the first slash).
    domain = cleaned.split("/")[0]
    # Take the main label before the TLD, e.g. "google" from "google.com".
    parts = domain.split(".")
    if len(parts) >= 2:
        return parts[-2].capitalize()
    return domain.capitalize() if domain else url
