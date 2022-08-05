from typing import List

import defusedxml.ElementTree as ET

from CTnlp.patient.patient import Patient


def load_patients_from_xml(
    patient_file: str, input_type: str = "TREC"
) -> List[Patient]:
    """Parses patients data from a single XML file and creates a Patient class instance
     for each parsed item.

    :param patient_file: str
    :param input_type: str describes the type of parser that should be used.
    Currently only two types of xml files are supported: TREC-style and CSIRO-style.
    :return: List of patients
    """
    tree = ET.parse(patient_file)
    root = tree.getroot()

    patients = []
    if input_type == "TREC":
        for elem in root:
            patients.append(
                Patient(
                    patient_id=int(elem.attrib["number"]), description=elem.text.strip()
                )
            )
    elif input_type == "CSIRO":
        for elem in root:
            patients.append(
                Patient(
                    patient_id=int(elem.attrib["number"]),
                    description=elem[0].text.strip(),
                )
            )
    else:
        raise ValueError("input_type can be only TREC or CSIRO")

    return patients
