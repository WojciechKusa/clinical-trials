import unittest
import xml.etree.ElementTree as ET

from CTnlp.parsers import parse_eligibility
from CTnlp.utils import Gender

sample_eligibility = """<?xml version="1.0" encoding="UTF-8"?>
<clinical_study>
  <eligibility>
    <criteria>
      <textblock>
        Inclusion Criteria:&#xD;
&#xD;
          -  Patients are required to meet the criteria of the American College of Rheumatology&#xD;
             (ACR)for rheumatoid arthritis.&#xD;
&#xD;
          -  Patients should be in functional class II, or III according to the criteria of the&#xD;
             ACR.&#xD;
&#xD;
          -  All candidates must be unsuccessfully treated (lack of efficacy) with at least two of&#xD;
             the following disease-modifying antirheumatic drugs: hydroxychloroquinine, oral or&#xD;
             injectable gold, methotrexate, azathioprine, penicillamine, and sulfasalazine.&#xD;
&#xD;
          -  Patients receiving nonsteroidal antiinflammatory drugs (NSAIDs), corticosteroids (&lt;=&#xD;
             10 mg per day), or both are eligible if the dosage has been stable for at least four&#xD;
             weeks before treatment and remained so throughout the study and follow-up period (the&#xD;
             use of narcotics for pain flares is allowed).&#xD;
&#xD;
          -  The necessary degree of disease activity at enrollment should be confirmed by a&#xD;
             finding of 10 or more swollen joints, 12 or more tender joints, and one of the&#xD;
             following two criteria: a Westergren erythrocyte sedimentation rate of at least 28 mm&#xD;
             per hour or a serum C-reactive protein level of more than 2.0 mg per deciliter; or&#xD;
             morning stiffness for at least 60 minutes.&#xD;
&#xD;
          -  Patients must have adequate bone marrow function, adequate liver function, adequate&#xD;
             renal function, calcium and electrolytes.&#xD;
&#xD;
          -  Patients must have a dobutamine stress ECHO, or exercise cardiac MUGA, or exercise&#xD;
             ECHO scan prior to entry and must fulfill certain criteria to be eligible. The spirit&#xD;
             of the criteria are to rule out organic heart disease.&#xD;
&#xD;
          -  Respiratory status: Patients who have FEV1 of &gt;= 60% of predicted, as well as a&#xD;
             maximum voluntary volume (MVV) of &gt;= 60% of predicted, and blood gases with a PO2 of&#xD;
             &gt;= 60 or oxygen saturation of &gt;= 90% are eligible.&#xD;
      </textblock>
    </criteria>
    <gender>All</gender>
    <minimum_age>18 Years</minimum_age>
    <maximum_age>65 Years</maximum_age>
    <healthy_volunteers>No</healthy_volunteers>
  </eligibility>
</clinical_study>
"""


class TestEligibilityCriteriaParser(unittest.TestCase):
    """Test eligibility criteria parser."""

    root = ET.fromstring(sample_eligibility)
    (
        gender,
        minimum_age,
        maximum_age,
        healthy_volunteers,
        criteria,
        inclusion,
        exclusion,
    ) = parse_eligibility(root=root)

    def test_gender(self):
        self.assertEqual(Gender.all, self.gender)

    def test_minimum_age(self):
        self.assertEqual(18, self.minimum_age)

    def test_maximum_age(self):
        self.assertEqual(65, self.maximum_age)

    def test_healthy_volunteers(self):
        self.assertEqual(False, self.healthy_volunteers)

    def test_inclusion_first_item(self):
        self.assertEqual(
            (
                " Patients are required to meet the criteria of the American College "
                + "of Rheumatology (ACR)for rheumatoid arthritis. "
            ),
            self.inclusion[0],
        )

    def test_inclusion_length(self):
        """test if number of extracted inclusion criteria matches expected."""
        self.assertEqual(8, len(self.inclusion))

    def test_exclusion_first_item(self):
        try:
            extracted_exclusion = self.exclusion[0]
        except IndexError:
            extracted_exclusion = None
        self.assertEqual(None, extracted_exclusion)

    def test_exclusion_length(self):
        """test if number of extracted exclusion criteria matches expected."""
        self.assertEqual(0, len(self.exclusion))


if __name__ == "__main__":
    unittest.main()
