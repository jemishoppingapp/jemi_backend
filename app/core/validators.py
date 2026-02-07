import re
from typing import Optional


def validate_nigerian_phone(phone: str) -> bool:
    """
    Validate Nigerian phone number format.
    
    Accepted formats:
    - +234XXXXXXXXXX (14 chars, international with +)
    - 234XXXXXXXXXX (13 chars, international without +)
    - 0XXXXXXXXXX (11 chars, local format)
    
    Nigerian mobile prefixes: 070, 080, 081, 090, 091 (MTN, Glo, Airtel, 9mobile)
    """
    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    
    patterns = [
        r"^\+234[789][01]\d{8}$",  # +234 format
        r"^234[789][01]\d{8}$",    # 234 format (no +)
        r"^0[789][01]\d{8}$",      # Local format
    ]
    
    return any(re.match(p, cleaned) for p in patterns)


def normalize_phone(phone: str) -> str:
    """
    Normalize Nigerian phone number to +234 format.
    
    Examples:
    - 08012345678 -> +2348012345678
    - 2348012345678 -> +2348012345678
    - +2348012345678 -> +2348012345678
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r"[^\d+]", "", phone)
    
    # Remove leading +
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    
    # If starts with 0, replace with 234
    if cleaned.startswith("0"):
        cleaned = "234" + cleaned[1:]
    
    # Ensure 234 prefix
    if not cleaned.startswith("234"):
        cleaned = "234" + cleaned
    
    return "+" + cleaned


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    return True, None


def generate_order_number() -> str:
    """Generate a unique order number."""
    import random
    import string
    from datetime import datetime
    
    # Format: JM + YYYYMMDD + 4 random digits
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = "".join(random.choices(string.digits, k=4))
    return f"JM{date_part}{random_part}"


def generate_pickup_code() -> str:
    """Generate a 6-digit pickup verification code."""
    import random
    return "".join(random.choices("0123456789", k=6))
