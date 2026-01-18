import re
from datetime import datetime
from typing import Optional


def parse_lifespan(lifespan_str: Optional[str]) -> Optional[int]:
    """
    Extract the lowest number from a lifespan string.
    Examples:
        "10-12 years" -> 10
        "up to 41 years" -> 41
        "from 2 to 5 years" -> 2
    Returns None if no number is found.
    """
    if not lifespan_str:
        return None

    # Find all numbers in the string
    numbers = re.findall(r'\d+', lifespan_str)
    if not numbers:
        return None

    # Return the lowest number as an integer
    return min(int(num) for num in numbers)


def parse_attributes(temperament: Optional[str], group_behavior: Optional[str]) -> list[str]:
    """
    Parse attributes from temperament (preferred) or group_behavior fields.
    Split by spaces and remove punctuation.
    Returns empty list if neither field exists.
    """
    # Prefer temperament over group_behavior
    text = temperament if temperament else group_behavior
    if not text:
        return []

    # Remove punctuation and split into words
    # Keep only alphanumeric characters and spaces
    cleaned = re.sub(r'[^\w\s]', ' ', text)
    words = cleaned.split()

    return words


def validate_date_format(date_str: str) -> bool:
    """
    Validate date format: DD-MM-YYYY
    Returns True if valid, False otherwise.
    """
    if date_str == "NA":
        return True

    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False


def compare_dates(date1: str, date2: str) -> int:
    """
    Compare two dates in DD-MM-YYYY format.
    Returns:
        -1 if date1 < date2
        0 if date1 == date2
        1 if date1 > date2
    Raises ValueError if dates are invalid.
    """
    if date1 == "NA" or date2 == "NA":
        raise ValueError("Cannot compare dates with 'NA'")

    d1 = datetime.strptime(date1, "%d-%m-%Y")
    d2 = datetime.strptime(date2, "%d-%m-%Y")

    if d1 < d2:
        return -1
    elif d1 > d2:
        return 1
    else:
        return 0


def generate_picture_filename(pet_name: str, pet_type: str, extension: str) -> str:
    """
    Generate a unique picture filename.
    Example: "Jamie-poodle-1234567890.jpg"
    """
    import time
    timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
    clean_name = re.sub(r'[^\w\s-]', '', pet_name).strip().replace(' ', '-')
    clean_type = re.sub(r'[^\w\s-]', '', pet_type).strip().replace(' ', '-')
    return f"{clean_name}-{clean_type}-{timestamp}.{extension}"
