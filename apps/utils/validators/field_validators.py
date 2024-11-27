import re

from fastapi import HTTPException, Form
from starlette import status

from utils.translations import trans as _


def validate_phone_format(phone_number: str) -> str:
    """
    Dynamically validate and normalize Uzbek phone numbers.

    Args:
        phone_number (str): The phone number input by the user.

    Returns:
        str: The normalized phone number in the format +998xxxxxxxxx.

    Raises:
        ValueError: If the phone number format is invalid.
    """
    cleaned_number = re.sub(r'\D', '', phone_number)

    if cleaned_number.startswith('998'):
        if len(cleaned_number) == 12:  # Correct format
            return f"+{cleaned_number}"
        else:
            raise ValueError("Phone number error: must be +998xxxxxxxxx")

    elif len(cleaned_number) == 9:
        return f"+998{cleaned_number}"

    elif len(cleaned_number) < 9:
        raise ValueError("Phone number error: must include +998xxxxxxxxx")

    else:
        raise ValueError("Phone number error: Invalid format.")


def validate_password(password: str) -> str:
    """Validate the password in a single pass with early exits."""
    if len(password) < 8:
        raise ValueError(_("Password must be at least 8 characters long."))

    has_upper = has_lower = has_digit = has_special = False
    specials = set("!@#$%^&*(),.?\":{}|<>")

    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in specials:
            has_special = True

        if has_upper and has_lower and has_digit and has_special:
            return password

    if not has_upper:
        raise ValueError(_("Password must contain at least one uppercase letter."))
    if not has_lower:
        raise ValueError(_("Password must contain at least one lowercase letter."))
    if not has_digit:
        raise ValueError(_("Password must contain at least one digit."))
    if not has_special:
        raise ValueError(_("Password must contain at least one special character."))

    return password


def validated_redirect_url(redirect_url: str = Form(...)):
    pattern = r'^(https|[a-zA-Z][a-zA-Z0-9+.-]*):\/\/[a-zA-Z0-9.-]+(\/[a-zA-Z0-9._~%!$&\'()*+,;=:@\/?]*)?$'

    if not re.match(pattern, redirect_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_("Invalid (deep) link. Must follow deep link format: <scheme>://<host>/<path>?<query"),
        )

    if redirect_url.startswith('http:'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_("Invalid URL scheme: 'http:' found. Expected 'https:' instead.")
        )

    return redirect_url


def validate_redirect_url_on_update(redirect_url: str = Form(None)):
    if not redirect_url:
        return redirect_url
    return validated_redirect_url(redirect_url)
