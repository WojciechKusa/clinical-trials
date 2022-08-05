from dataclasses import dataclass
from typing import Union, List, Optional

from CTnlp.utils import Gender


@dataclass
class Patient:
    """dataclass containing patient data."""

    patient_id: int
    description: str

    conditions: Optional[List[str]] = None
    gender: Gender = Gender.unknown
    age: Union[int, float, None] = None
    is_healthy: Optional[bool] = None
