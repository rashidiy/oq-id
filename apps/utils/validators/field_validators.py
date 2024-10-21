import re

from fastapi import HTTPException, Form
from starlette import status

from utils.translations import trans as _


def validate_phone_format(phone_number: str) -> str:
    """Validate and normalize the phone number format for Uzbek numbers."""

    cleaned_number = re.sub(r'\D', '', phone_number)

    if cleaned_number.startswith('998'):
        cleaned_number = cleaned_number[3:]

    if len(cleaned_number) == 9:
        return f'+998{cleaned_number}'

    if len(cleaned_number) == 2:
        return f'+998{cleaned_number}'

    raise ValueError(_("Invalid phone number format. Use formats like +998 xx xxx xx xx"))


def validate_password(password: str) -> str:
    """Validate the password according to specified rules."""
    if len(password) < 8:
        raise ValueError(_("Password must be at least 8 characters long."))

    if not re.search(r'[A-Z]', password):
        raise ValueError(_("Password must contain at least one uppercase letter."))

    if not re.search(r'[a-z]', password):
        raise ValueError(_("Password must contain at least one lowercase letter."))

    if not re.search(r'[0-9]', password):
        raise ValueError(_("Password must contain at least one digit."))

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
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
