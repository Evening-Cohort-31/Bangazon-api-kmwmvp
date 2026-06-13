"""Custom password validators for the Bangazon API application."""

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class StrongPasswordValidator:
    """Require at least one uppercase letter, lowercase letter, digit, and symbol."""

    def validate(self, password, user=None):
        errors = []

        if not re.search(r"[A-Z]", password):
            errors.append(_("Password must contain at least one uppercase letter."))
        if not re.search(r"[a-z]", password):
            errors.append(_("Password must contain at least one lowercase letter."))
        if not re.search(r"\d", password):
            errors.append(_("Password must contain at least one number."))
        if not re.search(r"[!@#$%^&*()\-_=+\[\]{}|;:'\",.<>?/`~\\]", password):
            errors.append(_("Password must contain at least one symbol."))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one number, and one symbol."
        )


class CreditCardValidator:
    """Validate that a credit card number is in the correct format."""

    def validate(self, card_number):
        if not re.fullmatch(r"\d{13,19}", card_number):
            raise ValidationError(
                _("Credit card number must be between 13 and 19 digits.")
            )

    def get_help_text(self):
        return _("Credit card number must be between 13 and 19 digits.")


class CreditCardDateValidator:
    """Validate that a credit card expiration date is in the correct format."""

    def validate(self, expiration_date):
        if not re.fullmatch(r"(0[1-9]|1[0-2])/\d{2}", expiration_date):
            raise ValidationError(
                _("Expiration date must be in the format MM/YY with a valid month.")
            )

    def get_help_text(self):
        return _("Expiration date must be in the format MM/YY with a valid month.")
