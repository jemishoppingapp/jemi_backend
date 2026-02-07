from datetime import datetime
from decimal import Decimal
from typing import Union
import re
import unicodedata


def format_naira(amount: Union[int, float, Decimal], include_symbol: bool = True) -> str:
    """
    Format amount as Nigerian Naira.
    
    Examples:
    - 12500 -> "₦12,500"
    - 1000000 -> "₦1,000,000"
    """
    if isinstance(amount, Decimal):
        amount = float(amount)
    
    formatted = f"{amount:,.0f}"
    
    if include_symbol:
        return f"₦{formatted}"
    return formatted


def format_date(dt: datetime, format_type: str = "short") -> str:
    """
    Format datetime for display.
    
    Format types:
    - short: "Jan 25, 2025"
    - long: "January 25, 2025"
    - full: "Saturday, January 25, 2025"
    - time: "2:30 PM"
    - datetime: "Jan 25, 2025 at 2:30 PM"
    """
    formats = {
        "short": "%b %d, %Y",
        "long": "%B %d, %Y",
        "full": "%A, %B %d, %Y",
        "time": "%I:%M %p",
        "datetime": "%b %d, %Y at %I:%M %p",
        "iso": "%Y-%m-%dT%H:%M:%S",
    }
    
    return dt.strftime(formats.get(format_type, formats["short"]))


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Examples:
    - "Basic Tee" -> "basic-tee"
    - "Wireless Earbuds (White)" -> "wireless-earbuds-white"
    """
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    
    # Remove leading/trailing hyphens
    text = text.strip("-")
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rsplit(" ", 1)[0] + suffix
