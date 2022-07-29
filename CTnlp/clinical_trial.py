from dataclasses import dataclass
from typing import List, Optional

from CTnlp.utils import Gender


@dataclass
class ClinicalTrial:
    """ClinicalTrial is a wrapper class that contains most important fields
    from the ClicnialTrials xml dump file.

    text is a variable containing elements from title, description and criteria.
    text_preprocessed contains tokenized and preprocessed text."""

    org_study_id: str
    nct_id: str  # primary id
    brief_title: str
    official_title: str
    summary: str
    description: str
    criteria: str
    inclusion: List[str]
    exclusion: List[str]
    gender: Gender
    minimum_age: Optional[int, float]
    maximum_age: Optional[int, float]
    healthy_volunteers: bool  # True means accept healthy
    text: str
    primary_outcome: str
    secondary_outcome: str

    # text which was preprocessed and is already tokenized
    text_preprocessed: Optional[List[str]] = None
