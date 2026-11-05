"""Helpers for cleaning messy customer and order fields."""
from __future__ import annotations

import re
from datetime import date, datetime

_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d %b %Y")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_name(name: str) -> str:
    """Trim, collapse inner whitespace and title-case a name."""
    return " ".join(name.split()).title()


def parse_amount(value: str) -> float | None:
    """Parse amounts like '12,50', '9.90 €' or '12.50'. Return None if invalid."""
    text = str(value).replace("€", "").replace(",", ".").strip()
    try:
        return float(text)
    except ValueError:
        return None


def parse_date(value: str) -> date | None:
    """Parse ISO, dd/mm/yyyy or '5 Mar 2024' dates. Return None if invalid."""
    text = str(value).strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def valid_email(email: str) -> bool:
    """Basic shape check: something@domain.tld."""
    return bool(_EMAIL_RE.match(str(email).strip()))
