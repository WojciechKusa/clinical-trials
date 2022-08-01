import os
import unittest

import defusedxml.ElementTree as ET

from CTnlp.parsers import parse_clinical_trial
from CTnlp.utils import Gender

HERE = os.path.dirname(os.path.abspath(__file__))

input_data = os.path.join(HERE, "../test_data/NCT00000102.xml")


class TestCriteriaParserFromFile(unittest.TestCase):
    """Test eligibility criteria parser."""

    root = ET.parse(input_data).getroot()
    clinical_trial = parse_clinical_trial(root=root)

    def test_org_study_id(self):
        self.assertEqual("NCRR-M01RR01070-0506", self.clinical_trial.org_study_id)

    def test_nct_id(self):
        self.assertEqual("NCT00000102", self.clinical_trial.nct_id)

    def test_brief_title(self):
        self.assertEqual(
            "Congenital Adrenal Hyperplasia: Calcium Channels as Therapeutic Targets",
            self.clinical_trial.brief_title,
        )

    def test_official_title(self):
        self.assertEqual(
            "",
            self.clinical_trial.official_title,
        )

    def test_study_type(self):
        self.assertEqual("Interventional", self.clinical_trial.study_type)

    def test_inclusion_length(self):
        """test if number of extracted inclusion criteria matches expected."""
        self.assertEqual(2, len(self.clinical_trial.inclusion))

    def test_exclusion_length(self):
        """test if number of extracted exclusion criteria matches expected."""
        self.assertEqual(2, len(self.clinical_trial.exclusion))

    def test_gender(self):
        self.assertEqual(Gender.all, self.clinical_trial.gender)

    def test_minimum_age(self):
        self.assertEqual(14, self.clinical_trial.minimum_age)

    def test_maximum_age(self):
        self.assertEqual(35, self.clinical_trial.maximum_age)

    def test_healthy_volunteers(self):
        self.assertEqual(False, self.clinical_trial.accepts_healthy_volunteers)

    def test_primary_outcomes_size(self):
        self.assertEqual(0, len(self.clinical_trial.primary_outcomes))

    def test_secondary_outcomes_size(self):
        self.assertEqual(0, len(self.clinical_trial.secondary_outcomes))

    def test_conditions_size(self):
        self.assertEqual(1, len(self.clinical_trial.conditions))

    def test_conditions(self):
        for _condition, expected in zip(
            self.clinical_trial.conditions, ["Congenital Adrenal Hyperplasia"]
        ):
            self.assertEqual(_condition, expected)

    def test_interventions_size(self):
        self.assertEqual(1, len(self.clinical_trial.interventions))


if __name__ == "__main__":
    unittest.main()
