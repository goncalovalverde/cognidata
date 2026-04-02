"""
Password strength validation for CogniData security
Enforces GDPR Article 32 and OWASP password guidelines
"""

import re
from typing import Tuple


class PasswordStrengthError(Exception):
    """Raised when password doesn't meet minimum strength requirements"""
    pass


class PasswordValidator:
    """
    Password strength validator for admin password setup.

    Requirements (OWASP + GDPR Article 32):
    - Minimum 12 characters
    - At least 1 uppercase letter (A-Z)
    - At least 1 lowercase letter (a-z)
    - At least 1 digit (0-9)
    - At least 1 special character (!@#$%^&*)
    """

    MIN_LENGTH = 12
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    @staticmethod
    def validate(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        Returns (is_valid: bool, message: str)
        """
        if not password:
            return False, "Password cannot be empty."

        # Check length
        if len(password) < PasswordValidator.MIN_LENGTH:
            return (
                False,
                f"Password must be at least {PasswordValidator.MIN_LENGTH} characters long. "
                f"Currently {len(password)} characters.",
            )

        # Check for uppercase
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least 1 uppercase letter (A-Z)."

        # Check for lowercase
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least 1 lowercase letter (a-z)."

        # Check for digit
        if not re.search(r"\d", password):
            return False, "Password must contain at least 1 digit (0-9)."

        # Check for special character
        if not re.search(rf"[{re.escape(PasswordValidator.SPECIAL_CHARS)}]", password):
            special_list = ", ".join(list(PasswordValidator.SPECIAL_CHARS)[:10]) + ", ..."
            return (
                False,
                f"Password must contain at least 1 special character ({special_list})",
            )

        return True, "Password strength: OK ✅"

    @staticmethod
    def validate_or_raise(password: str) -> None:
        """Validate password and raise PasswordStrengthError if invalid"""
        is_valid, message = PasswordValidator.validate(password)
        if not is_valid:
            raise PasswordStrengthError(message)

    @staticmethod
    def get_strength_feedback(password: str) -> str:
        """Get detailed feedback on password strength"""
        feedback = []

        if len(password) < PasswordValidator.MIN_LENGTH:
            feedback.append(
                f"❌ Length: {len(password)}/{PasswordValidator.MIN_LENGTH} characters"
            )
        else:
            feedback.append(f"✅ Length: {len(password)} characters")

        if re.search(r"[A-Z]", password):
            feedback.append("✅ Uppercase letter present")
        else:
            feedback.append("❌ Missing uppercase letter (A-Z)")

        if re.search(r"[a-z]", password):
            feedback.append("✅ Lowercase letter present")
        else:
            feedback.append("❌ Missing lowercase letter (a-z)")

        if re.search(r"\d", password):
            feedback.append("✅ Digit present")
        else:
            feedback.append("❌ Missing digit (0-9)")

        if re.search(rf"[{re.escape(PasswordValidator.SPECIAL_CHARS)}]", password):
            feedback.append("✅ Special character present")
        else:
            feedback.append("❌ Missing special character")

        return "\n".join(feedback)
