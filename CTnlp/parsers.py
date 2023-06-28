"""Module containing parsers for clinical trials file"""
import copy
import logging
import os
import re
from glob import glob
from typing import List, Optional, Tuple, Dict

import defusedxml.ElementTree as ET
import tqdm

from CTnlp.clinical_trial import ClinicalTrial, Intervention
from CTnlp.utils import Gender


def _safe_get_item(root: ET, tag_name: str, default: str = "") -> str:
    """Returns text from the first element with tag_name in root."""
    try:
        return root.find(tag_name).text
    except AttributeError:
        return default


def _safe_get_nested_item(root: ET, tag_name: str, default: str = "") -> str:
    """Returns text from the first element with tag_name in root."""
    result = root.find(tag_name)
    if result:
        result = result[0].text

    if not result:
        result = default

    return result


def get_criteria(criteria_string: str) -> List[str]:
    """Parses inclusion or exclusion criteria string and returns a list of criteria.

    :param criteria_string:
    :return:
    """
    criteria_list: List[str] = []

    if criteria_string.strip():
        for criterion in re.split(r" - | \d\. ", criteria_string):
            if criterion.strip() and criterion.strip() != ":":
                criterion = re.sub(r"[\r\n\t ]+", " ", criterion)
                criteria_list.append(criterion.strip())

    return criteria_list


def parse_criteria(criteria: str) -> Optional[Tuple[List[str], List[str]]]:
    """Parses the criteria xml element to find and extract inclusion and
    exclusion criteria for a study.

    It uses heuristics defined based on the dataset:
    - incl/excl criteria start with a header and are sorted inclusion first,
    - every criterion starts from a newline with a number or a '-' character.

    :param criteria: element with criteria string
    :return: tuple with inclusion and exclusion criteria lists. If criteria
             cannot be parsed, returns None.
    """

    def _split_criteria(text: str, header: str) -> Tuple[str, str]:
        """Splits the criteria text based on the given header."""
        regex_header = re.compile(re.escape(header), re.IGNORECASE)
        match = regex_header.search(text)
        if match:
            start_index = match.start()
            return text[:start_index], text[start_index + len(match.group()) :]
        return text, ""

    inclusion_headers = [
        "inclusion criteria",
        "inclusive criteria",
    ]
    exclusion_headers = [
        "eclusion criteria",
        "exclusion critieria",
        "exclusion criteria",
        "exclusive criteria",
    ]
    criteria_text = copy.copy(criteria)

    # Splitting the text based on inclusion headers
    inclusion_text = ""
    pre_inclusion_text = ""
    for inclusion_header in inclusion_headers:
        pre_inclusion_text, inclusion_text = _split_criteria(
            criteria_text, inclusion_header
        )
        if inclusion_text:
            break

    if pre_inclusion_text.strip().lower() not in ["", "key", "-", "main"]:
        logging.debug(
            "parse_criteria: parser is skipping text found before inclusion split: %s",
            pre_inclusion_text.strip(),
        )
    if not inclusion_text:
        return None

    # Splitting the remaining text based on exclusion headers
    exclusion_text = ""
    for exclusion_header in exclusion_headers:
        inclusion_text, exclusion_text = _split_criteria(
            inclusion_text, exclusion_header
        )
        if exclusion_text:
            break

    inclusion_criteria = get_criteria(inclusion_text)
    exclusion_criteria = get_criteria(exclusion_text)

    return inclusion_criteria, exclusion_criteria


def parse_age(age_string: str) -> Optional[float]:
    """Parses age from string to a float number of years.

    :param age_string: string with age from clinical trial
    :return: Returns age or None if age cannot be parsed or does not exist.
    """
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
    """Parse

    :param gender_string:
    :return:
    """
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
) -> Tuple[Gender, Optional[float], Optional[float], bool, str, List[str], List[str]]:
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
        minimum_age = getattr(eligibility.find("minimum_age"), "text", "")
        maximum_age = getattr(eligibility.find("maximum_age"), "text", "")
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
    primary_outcomes: List[str] = []
    secondary_outcomes: List[str] = []
    if primarys := root.findall("primary_outcome"):
        primary_outcomes.extend(
            getattr(primary.find("measure"), "text", "") for primary in primarys
        )

    if secondarys := root.findall("secondary_outcome"):
        secondary_outcomes.extend(
            getattr(secondary.find("measure"), "text", "") for secondary in secondarys
        )

    return primary_outcomes, secondary_outcomes


def get_conditions(root: ET) -> List[str]:
    return [condition.text for condition in root.findall("condition")]


def get_interventions(root: ET) -> List[Intervention]:
    return [
        Intervention(
            type=_safe_get_item(root=_intervention, tag_name="intervention_type"),
            name=_safe_get_item(root=_intervention, tag_name="intervention_name"),
            description=_safe_get_item(root=_intervention, tag_name="description"),
        )
        for _intervention in root.findall("intervention")
    ]


def parse_clinical_trial(root: ET) -> ClinicalTrial:
    org_study_id = getattr(
        root.find("id_info").find("org_study_id"), "text", "empty_org_study_id"
    )
    nct_id = getattr(root.find("id_info").find("nct_id"), "text", "empty_nct_id")

    brief_summary = _safe_get_nested_item(root=root, tag_name="brief_summary")
    description = _safe_get_nested_item(root=root, tag_name="detailed_description")
    brief_title = _safe_get_item(root=root, tag_name="brief_title")
    official_title = _safe_get_item(root=root, tag_name="official_title")
    study_type = _safe_get_item(root=root, tag_name="study_type")

    conditions = get_conditions(root=root)
    interventions = get_interventions(root=root)

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
        primary_outcomes=primary_outcomes,
        secondary_outcomes=secondary_outcomes,
        study_type=study_type,
        conditions=conditions,
        interventions=interventions,
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
        try:
            tree = ET.parse(file)
        except ET.ParseError:
            logging.error("Skipping file %s", file)
            continue
        root = tree.getroot()
        clinical_trial = parse_clinical_trial(root=root)
        clinical_trials.append(clinical_trial)

    if len(files) > 0:
        total_parsed = 0

        logging.info(
            "percentage of successfully parsed criteria: %f", total_parsed / len(files)
        )

    return clinical_trials
