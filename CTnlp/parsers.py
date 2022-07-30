"""Module containing parsers for clinical trials file"""
import logging
import os
import re
import xml.etree.ElementTree as ET
from glob import glob
from typing import List, Optional, Tuple, Union

import tqdm

from CTnlp.clinical_trial import ClinicalTrial
from CTnlp.utils import Gender


def safe_get_item(item_name: str, root: ET) -> str:
    return item.text if (item := root.find(item_name)) else ""


def get_criteria(criteria_string: str) -> List[str]:
    criteria_list: List[str] = []

    if criteria_string.strip():
        for criterion in re.split(r" - | \d\. ", criteria_string):
            if criterion.strip() and criterion.strip() != ":":
                criterion = re.sub(r"[\r\n\t ]+", " ", criterion)
                criteria_list.append(criterion.strip())

    return criteria_list


def parse_criteria(criteria: str) -> Optional[Tuple[List[str], List[str]]]:
    """Tries to parse the criteria xml element to find and extract inclusion and
    exclusion criteria for a study.
    It uses heuristics defined based on the dataset:
    - incl/excl criteria start with a header and are sorted inclusion first,
    - every criterion starts from a newline with a number or a '-' character.

    :param criteria:
    :return: if couldn't find any criteria returns None
    """
    inclusion_criteria_strings = [
        "Inclusion Criteria",
        "Inclusion criteria",
        "Inclusive criteria",
        "INCLUSION CRITERIA",
    ]
    for inclusion_criteria_string in inclusion_criteria_strings:
        if inclusion_criteria_string in criteria:
            criteria_after_split = criteria.split(inclusion_criteria_string)
            break
        else:
            criteria_after_split = criteria

    if len(criteria_after_split) == 2:
        empty, tmp_inclusion = criteria_after_split
    else:
        return None
    if empty.strip().lower() not in ["", "key", "-", "main"]:
        logging.debug(
            "parse_criteria: skipping not parsed text after split: %s", empty.strip()
        )

    exclusion_criteria_strings = [
        "Exclusion Criteria",
        "Exclusion criteria",
        "Exclusive criteria",
        "EXCLUSION CRITERIA",
        "ECLUSION CRITERIA",
        "EXCLUSION CRITIERIA",
    ]
    for exclusion_criteria_string in exclusion_criteria_strings:
        if tmp_inclusion.find(exclusion_criteria_string) != -1:
            inclusion_exclusion_split = tmp_inclusion.split(exclusion_criteria_string)
            break
        else:
            inclusion_exclusion_split = [tmp_inclusion]

    exclusion = ""
    if len(inclusion_exclusion_split) == 2:
        inclusion, exclusion = inclusion_exclusion_split
    elif len(inclusion_exclusion_split) == 1:
        inclusion = inclusion_exclusion_split[0]
    else:
        return None

    inclusions = get_criteria(criteria_string=inclusion)
    if len(inclusions) == 0:
        return None
    exclusions = get_criteria(criteria_string=exclusion)

    return inclusions, exclusions


def parse_age(age_string: str) -> Optional[float]:
    if not age_string:
        return None
    if age_string in {"N/A", "None"}:
        return None

    age_patterns: Dict[str, int] = {
        r"(\d{1,3}) Year[s]?": 1,
        r"(\d{1,3}) Month[s]?": 12,
        r"(\d{1,3}) Week[s]?": 52,
        r"(\d{1,3}) Day[s]?": 365,
        r"(\d{1,3}) Hour[s]?": 8766,
        r"(\d{1,3}) Minute[s]?": 525960,
    }
    for pattern, denominator in age_patterns.items():
        match = re.search(re.compile(pattern, flags=re.IGNORECASE), age_string)
        if match is not None:
            return int(match[1]) / denominator

    logging.warning("couldn't parse age from %s", age_string)
    return None


def parse_gender(gender_string: Optional[str]) -> Gender:
    if gender_string == "All":
        return Gender.all
    elif gender_string == "Male":
        return Gender.male
    elif gender_string == "Female":
        return Gender.female
    else:
        return Gender.unknown  # most probably gender criteria were empty


def parse_health_status(healthy_volunteers: Optional[str]) -> bool:  # sourcery skip
    if healthy_volunteers == "Accepts Healthy Volunteers":
        return True
    elif healthy_volunteers == "No":
        return False
    else:
        # if there is no data to exclude a patient we assume
        # that it is possible to include healthy
        return True


def parse_eligibility(
    root: ET,
) -> Tuple[Gender, int, int, bool, str, List[str], List[str]]:
    inclusion: List[str] = []
    exclusion: List[str] = []
    if eligibility := root.find("eligibility"):
        criteria = eligibility.find("criteria")
        if criteria:
            criteria = criteria[0].text
            if result := parse_criteria(criteria=criteria):
                inclusion = result[0]
                exclusion = result[1]
        else:
            criteria = ""

        gender = getattr(eligibility.find("gender"), "text", None)
        minimum_age = getattr(eligibility.find("minimum_age"), "text", None)
        maximum_age = getattr(eligibility.find("maximum_age"), "text", None)
        healthy_volunteers = getattr(
            eligibility.find("healthy_volunteers"), "text", None
        )

    else:
        criteria = ""
        gender = ""
        minimum_age = ""
        maximum_age = ""
        healthy_volunteers = ""
    gender = parse_gender(gender)
    print(minimum_age)
    minimum_age = parse_age(minimum_age)
    maximum_age = parse_age(maximum_age)
    healthy_volunteers = parse_health_status(healthy_volunteers)

    return (
        gender,
        minimum_age,
        maximum_age,
        healthy_volunteers,
        criteria,
        inclusion,
        exclusion,
    )


def get_outcomes(root: ET) -> Tuple[List[str], List[str]]:
    primary_outcomes = []
    secondary_outcomes = []
    if primarys := root.findall("primary_outcome"):
        primary_outcomes.extend(
            getattr(primary.find("measure"), "text", None) for primary in primarys
        )

    if secondarys := root.findall("secondary_outcome"):
        secondary_outcomes.extend(
            getattr(secondary.find("measure"), "text", None) for secondary in secondarys
        )

    return primary_outcomes, secondary_outcomes


def parse_clinical_trial(root: ET) -> ClinicalTrial:
    org_study_id = getattr(root.find("id_info").find("org_study_id"), "text", None)
    nct_id = getattr(root.find("id_info").find("nct_id"), "text", None)

    brief_summary = root.find("brief_summary")
    if brief_summary:
        brief_summary = brief_summary[0].text

    if not brief_summary:
        brief_summary = ""

    description = root.find("detailed_description")
    if description:
        description = description[0].text

    if not description:
        description = ""

    brief_title = safe_get_item(item_name="brief_title", root=root)
    official_title = safe_get_item(item_name="official_title", root=root)

    primary_outcomes, secondary_outcomes = get_outcomes(root=root)

    (
        gender,
        minimum_age,
        maximum_age,
        healthy_volunteers,
        criteria,
        inclusion,
        exclusion,
    ) = parse_eligibility(root=root)

    text: str = brief_title + official_title + brief_summary + criteria
    if not text.strip():
        text = "empty"

    return ClinicalTrial(
        org_study_id=org_study_id,
        nct_id=nct_id,
        brief_summary=brief_summary,
        detailed_description=description,
        criteria=criteria,
        gender=gender,
        minimum_age=minimum_age,
        maximum_age=maximum_age,
        accepts_healthy_volunteers=healthy_volunteers,
        inclusion=inclusion,
        exclusion=exclusion,
        brief_title=brief_title,
        official_title=official_title,
        text=text,
        primary_outcomes=primary_outcomes,
        secondary_outcomes=secondary_outcomes,
    )


def parse_clinical_trials_from_folder(
    folder_name: str, first_n: Optional[int] = None
) -> Optional[List[ClinicalTrial]]:
    files = [y for x in os.walk(folder_name) for y in glob(os.path.join(x[0], "*.xml"))]

    if not files:
        logging.error(
            "No files in a folder %s. Stopping parse_clinical_trials_from_folder",
            folder_name,
        )
        return None

    if first_n:
        files = files[:first_n]

    clinical_trials = []
    for file in tqdm.tqdm(files):
        tree = ET.parse(file)
        root = tree.getroot()
        clinical_trial = parse_clinical_trial(root=root)
        clinical_trials.append(clinical_trial)

    if len(files) > 0:
        total_parsed = 0

        logging.info(
            "percentage of successfully parsed criteria: %f", total_parsed / len(files)
        )

    return clinical_trials
