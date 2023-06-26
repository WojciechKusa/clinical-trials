"""Module containing functions that extract patient's past medical history and family
history from unstructured paragraphs of text.
TODO: cover more specific cases if history spans across multiple lines for
 all extractions.
"""
import re
from re import Match
from typing import Optional, Tuple


def extract_past_medical_history(patient_description: str) -> Optional[Match]:
    """Tries to extract a sentence from the patient description that corresponds to
    past medical history.
    :param patient_description: unstructured patient description without specific
        sections
    :return: re.Match object or None if didn't find anything
    """
    return (
        re.search(
            r"[!\.][^!\.]*medical history.*?\.", patient_description, re.IGNORECASE
        )
        or re.search(
            r"[!\.][^!\.]*has (no )?(a )?(positive )?history.*?\.",
            patient_description,
            re.IGNORECASE,
        )
        or re.search(
            r"[!\.][^!\.]*past medical history:?\n([\d|-]?[^\n]*\n)*",
            patient_description,
            re.IGNORECASE,
        )
    )


def extract_family_history(patient_description: str) -> Optional[Match]:
    """Extracts a sentence with family history using regex match

    :param patient_description: unstructured patient description without specific
            sections
    :return: re.Match object or None if didn't find anything
    """
    return re.search(r"\.[^\.]*family history.*?\.", patient_description, re.IGNORECASE)


def extract_sections(patient_description: str) -> Tuple[str, str, str]:
    """Function tries to extract sections form unstructured patient report and
    categories them into three: current medical history, past medical history
    and family history.

    :param patient_description: unstructured patient description without specific
            sections
    :return: Tuple of three strings containing current, past and family medical history
    """
    current_mh_text: str = patient_description
    past_mh_text: str = ""
    family_mh_text: str = ""

    pmh = extract_past_medical_history(patient_description)
    fh = extract_family_history(patient_description)

    if pmh and fh:
        if pmh.start() > fh.start():
            _first = fh
            _second = pmh
        else:
            _first = pmh
            _second = fh

        current_mh_text = (
            patient_description[: _second.start() + 2]
            + patient_description[_second.end() + 1 :]
        )
        current_mh_text = (
            current_mh_text[: _first.start() + 2] + current_mh_text[_first.end() + 1 :]
        )
        past_mh_text = patient_description[pmh.start() + 1 : pmh.end()].strip()
        family_mh_text = patient_description[fh.start() + 1 : fh.end()].strip()

    if pmh and not fh:
        current_mh_text = (
            patient_description[: pmh.start() + 2]
            + patient_description[pmh.end() + 1 :]
        )
        past_mh_text = patient_description[pmh.start() + 1 : pmh.end()].strip()

    if fh and not pmh:
        current_mh_text = (
            patient_description[: fh.start() + 2] + patient_description[fh.end() + 1 :]
        )
        family_mh_text = patient_description[fh.start() + 1 : fh.end()].strip()

    return current_mh_text, past_mh_text, family_mh_text
