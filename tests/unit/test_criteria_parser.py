"""Unit tests for the criteria parser module."""
import unittest

from CTnlp.parsers import parse_criteria

EXAMPLE_CRITERIA = """

        Inclusion Criteria:

          -  Subject must have histologically confirmed anaplastic astrocytoma on the tentorium at
             first relapse, and satisfy the following:

               -  unequivocal evidence of tumor recurrence or aggravation by MRI scan after
                  treatment for initial onset; the lesions must be measurable;

               -  anaplastic astrocytoma diagnosed histologically by the last pathological
                  diagnostic tests (including initial diagnosis) prior to initial administration of
                  temozolomide;

               -  tissue samples available for Central Pathologic Reviewer;

               -  pathologic diagnosis report by the study-conducting medical institution must be
                  available for the sponsor.

          -  MRI-related criteria:

               -  MRI scan performed within 14 days before initial temozolomide administration;

               -  assessable tumor site confirmed by MRI;

               -  dosage of steroidal agents not increased within 7 days before MRI prior to
                  initial temozolomide administration, except for postoperative subjects for first
                  relapse;

               -  MRI performed at the Principal Investigator's study location or designated
                  radiology facility during the study.

          -  Age >=18 years, either sex, inpatients or outpatients.

          -  Use of medically approved contraception methods in fertile subjects.

          -  Karnofsky performance status >=70.

          -  Adequate clinically laboratory values obtained within 14 days before initial
             temozolomide administration.

          -  Criteria regarding treatment of initial onset:

               -  tumor biopsy, regardless of tumor resection at initial diagnosis;

               -  prior radiation therapy;

               -  prior chemotherapy with up to one nitrosourea-containing regimen.

          -  Tumor may or may not have been surgically resected at first relapse, but residual
             measurable disease is required.

          -  For subjects who had surgical resection of tumor at first relapse:

               -  MRI scan must have been performed within 72 hours after surgery.

               -  the dose of steroidal agents must be reduced before temozolomide administration.

          -  Life expectancy >=12 weeks.

          -  Written informed consent obtained.

        Exclusion Criteria:

          -  History of treatment with dacarbazine.

          -  Subjects who received chemotherapy within 6 weeks before initial temozolomide
             administration.

          -  Subjects who received interstitial radiotherapy or stereotactic radiosurgery.

          -  Subjects who completed radiotherapy within 12 weeks before initial temozolomide
             administration.

          -  Surgery at first relapse (including biopsy) within 1 week before initial temozolomide
             administration.

          -  Subjects not recovered from acute toxicity due to previous therapy.

          -  High-risk subjects with complication of diseases other than malignant tumor, or who
             require systemic administration of antibiotics for infection.

          -  Previous or concurrent malignancies at other sites.

          -  Pregnant or nursing women.

          -  Women of childbearing potential not using an effective method of contraception.

          -  Subjects previously treated with temozolomide.

          -  Participation in an ongoing clinical study, or in other clinical studies within 6
             months before initial temozolomide administration.

          -  Subjects found inappropriate for the study by the investigator or subinvestigator.
      
"""


class TestCriteriaParser(unittest.TestCase):
    """Test parser of inclusion criteria"""

    inclusion, exclusion = parse_criteria(EXAMPLE_CRITERIA)

    def test_inclusion_length(self):
        """test if number of extracted inclusion criteria matches expected."""
        self.assertEqual(24, len(self.inclusion))

    def test_exclusion_length(self):
        """test if number of extracted exclusion criteria matches expected."""
        self.assertEqual(13, len(self.exclusion))

    def test_inclusion_type(self):
        """test if extracted inclusion criteria are of type str."""
        self.assertTrue(all(isinstance(x, str) for x in self.inclusion))

    def test_exclusion_type(self):
        """test if extracted exclusion criteria are of type str."""
        self.assertTrue(all(isinstance(x, str) for x in self.exclusion))


if __name__ == "__main__":
    unittest.main()
