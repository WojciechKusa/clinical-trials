from dataclasses import dataclass
from typing import List, Optional

from CTnlp.utils import Gender


@dataclass(frozen=True)
class Intervention:
    """dataclass modelling clinical trials' intervention."""

    type: str
    name: str
    description: Optional[str]


@dataclass
class ClinicalTrial:
    """ClinicalTrial is a wrapper class that contains most important fields
    from the ClicnialTrials xml dump file.

    text is a variable containing elements from title, detailed_description and criteria.
    text_preprocessed contains tokenized and preprocessed text."""

    org_study_id: str
    nct_id: str  # primary id

    brief_title: str
    official_title: str

    brief_summary: str
    detailed_description: str

    study_type: Optional[str]

    criteria: str
    inclusion: List[str]
    exclusion: List[str]
    gender: Gender
    minimum_age: Optional[float]
    maximum_age: Optional[float]
    accepts_healthy_volunteers: bool  # True means accept healthy

    primary_outcomes: Optional[List[str]]
    secondary_outcomes: Optional[List[str]]

    conditions: Optional[List[str]]
    interventions: Optional[List[Intervention]]

    # text which was preprocessed and is already tokenized
    text_preprocessed: Optional[List[str]] = None

    def text(self) -> str:
        """returns concatenated text of major fields in clinical trial."""
        _text = f"{self.brief_title.strip()} {self.official_title.strip()}\n"
        _text += f"{self.brief_summary.strip()} {self.detailed_description.strip()}\n"
        _text += f"{self.criteria.strip()}"
        return _text
