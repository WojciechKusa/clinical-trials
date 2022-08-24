import os
import unittest

from CTnlp.clinical_trial import ClinicalTrial
from CTnlp.parsers import parse_clinical_trials_from_folder

current_file_directory = os.path.dirname(os.path.abspath(__file__))

input_data = os.path.join(current_file_directory, "../test_data/trials")


class TestCriteriaParserFromFolder(unittest.TestCase):
    """Test eligibility criteria parser."""

    cts = parse_clinical_trials_from_folder(folder_name=input_data)

    def test_number_parsed_trials(self):
        self.assertEqual(1, len(self.cts))

    def test_type_of_trials(self):
        self.assertTrue(isinstance(self.cts, list))
        for _ct in self.cts:
            self.assertTrue(isinstance(_ct, ClinicalTrial))


if __name__ == "__main__":
    unittest.main()
