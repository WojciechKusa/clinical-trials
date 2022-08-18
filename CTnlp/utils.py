"""Module containing utility functions and classes."""
from enum import Enum


class Gender(str, Enum):
    """Enum type class for representing Gender in topics and clinical trials."""

    unknown = "U"
    male = "M"
    female = "F"
    all = "A"
