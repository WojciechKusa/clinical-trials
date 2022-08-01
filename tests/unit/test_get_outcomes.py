import unittest

import defusedxml.ElementTree as ET

from CTnlp.parsers import get_outcomes

outcomes_xml = """<?xml version="1.0" encoding="UTF-8"?>
<clinical_study>
  <primary_outcome>
    <measure>Effectiveness of L-glutamine for mucositis</measure>
    <time_frame>2 weeks after end of radiation treatment</time_frame>
    <description>Evaluate effectiveness of L-glutamine as compared to placebo in terms of: maximum toxicity grade during radiation treatment, mucositis toxicity grade 2 weeks after the end of radiation treatment, and patient reported worst mouth pain two weeks after the end of radiation treatment.</description>
  </primary_outcome>
  <secondary_outcome>
    <measure>Duration of severe mucositis, radiation treatment delay, and weight loss</measure>
    <time_frame>2 weeks after radiation treatment</time_frame>
  </secondary_outcome>
  <secondary_outcome>
    <measure>Toxicities</measure>
    <time_frame>within 2 weeks after radiation treatment</time_frame>
  </secondary_outcome>
</clinical_study>
"""


class TestGetOutcomes(unittest.TestCase):
    """Test get outcomes method"""

    root = ET.fromstring(outcomes_xml)
    primary_outcomes, secondary_outcomes = get_outcomes(root=root)

    def test_type_primary(self):
        """check if type of primary outcomes is list and items are strings."""
        self.assertTrue(isinstance(self.primary_outcomes, list))
        for _outcome in self.primary_outcomes:
            self.assertTrue(isinstance(_outcome, str))

    def test_type_secondary(self):
        """check if type of secondary outcomes is list."""
        self.assertTrue(isinstance(self.secondary_outcomes, list))
        for _outcome in self.secondary_outcomes:
            self.assertTrue(isinstance(_outcome, str))

    def test_size_primary(self):
        """check if type of secondary outcomes is list."""
        self.assertEqual(1, len(self.primary_outcomes))

    def test_size_secondary(self):
        """check if type of secondary outcomes is list."""
        self.assertEqual(2, len(self.secondary_outcomes))

    def test_content_primary(self):
        """check content of primary outcomes."""
        for _outcome, expected in zip(
            self.primary_outcomes, ["Effectiveness of L-glutamine for mucositis"]
        ):
            self.assertEqual(_outcome, expected)

    def test_content_secondary(self):
        """check content of secondary outcomes."""
        for _outcome, expected in zip(
            self.secondary_outcomes,
            [
                "Duration of severe mucositis, radiation treatment delay, and weight loss",
                "Toxicities",
            ],
        ):
            self.assertEqual(_outcome, expected)


if __name__ == "__main__":
    unittest.main()
