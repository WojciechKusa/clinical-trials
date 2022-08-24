from dataclasses import dataclass
from typing import Union, List, Optional

import defusedxml.ElementTree

from CTnlp.patient.parsers import extract_sections
from CTnlp.utils import Gender


@dataclass
class Patient:
    """dataclass containing patient data."""

    unique_id: str
    patient_id: int
    description: str

    conditions: Optional[List[str]] = None
    current_medical_history: Optional[str] = None
    past_medical_history: Optional[str] = None
    family_medical_history: Optional[str] = None

    gender: Gender = Gender.unknown
    age: Union[int, float, None] = None
    is_healthy: Optional[bool] = None
    is_smoker: Optional[bool] = None
    is_drinker: Optional[bool] = None


def load_patients_from_xml(
    patient_file: str, input_type: str = "TREC"
) -> List[Patient]:
    """Parses patients data from a single XML file and creates a Patient class instance
     for each parsed item.

    :param patient_file: str
    :param input_type: str describes the type of parser that should be used.
    Currently only two types of xml files are supported: TREC-style and CSIRO-style.
    :return: List of Patient objects
    """
    tree = defusedxml.ElementTree.parse(patient_file)
    filename = patient_file.split("/")[-1]
    root = tree.getroot()

    patients = []
    if input_type == "CSIRO":
        patients.extend(
            Patient(
                unique_id=f"{filename}_{elem.attrib['number']}",
                patient_id=int(elem.attrib["number"]),
                description=elem[0].text.strip(),
            )
            for elem in root
        )

    elif input_type == "TREC":
        patients.extend(
            Patient(
                unique_id=f"{filename}_{elem.attrib['number']}",
                patient_id=int(elem.attrib["number"]),
                description=elem.text.strip(),
            )
            for elem in root
        )
    else:
        raise ValueError("input_type can be only 'TREC' or 'CSIRO'")

    for patient in patients:
        current_mh_text, past_mh_text, family_mh_text = extract_sections(
            patient.description
        )
        patient.current_medical_history = current_mh_text
        patient.past_medical_history = past_mh_text
        patient.family_medical_history = family_mh_text

    return patients
