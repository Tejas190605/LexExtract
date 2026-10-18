"""
Centralized Role Definitions for LexExtract Role-Based Access Control (RBAC).
"""

from enum import Enum


class Role(str, Enum):
    USER = "USER"
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"

    @classmethod
    def has_value(cls, value: str) -> bool:
        if not value:
            return False
        return value.upper() in cls._value2member_map_

    @classmethod
    def normalize(cls, value: str) -> str:
        """
        Normalizes role string to canonical uppercase representation.
        Defaults to USER if unrecognized.
        """
        if not value:
            return cls.USER.value
        val_upper = value.strip().upper()
        if val_upper in cls._value2member_map_:
            return val_upper
        return cls.USER.value
