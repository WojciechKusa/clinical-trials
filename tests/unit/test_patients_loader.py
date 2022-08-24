import os
import unittest

import requests

from CTnlp.patient import load_patients_from_xml

headers = {
    "User-Agent": "Mozilla/5.0 Firefox/55.0",
}

URL = "http://www.trec-cds.org/topics2022.xml"
current_file_directory = os.path.dirname(os.path.abspath(__file__))

trec_topics = os.path.join(current_file_directory, "../test_data/trec_topics_2022.xml")

if not os.path.exists(trec_topics):
    with open(trec_topics, "wb") as f:
        f.write(requests.get(URL, headers=headers).content)


class TestPatientsLoader(unittest.TestCase):
    patients = load_patients_from_xml(trec_topics)

    def test_patients_size(self):
        self.assertEqual(50, len(self.patients))

    def test_description_first_patient_first_tokens(self):
        self.assertEqual("A 19-year-old", self.patients[0].description[:13])


if __name__ == "__main__":
    unittest.main()
