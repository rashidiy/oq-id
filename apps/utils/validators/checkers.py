import re

from utils.translations import trans as _


def validate_phone_format(phone_number: str) -> str:
    """Validate and normalize the Uzbek phone number format."""
    uzb_phone_regex = r'^(\+998|998)?(9[0-9]{1}|33|88|71)([- ]?)\d{3}([- ]?)\d{2}([- ]?)\d{2}$'
    cleaned_number = re.sub(r'\D', '', phone_number)

    if re.match(uzb_phone_regex, phone_number):
        if cleaned_number.startswith('998'):
            return f"+{cleaned_number}"
        elif len(cleaned_number) == 9:
            return f"+998{cleaned_number}"
        else:
            raise ValueError(_("Invalid phone number format."))
    else:
        raise ValueError(_("Invalid phone number format."))


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
