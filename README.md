# clinical-trials

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/f4ddceaeff734410a9ad5bb3b0bed2a4)](https://app.codacy.com/gh/WojciechKusa/clinical-trials?utm_source=github.com&utm_medium=referral&utm_content=WojciechKusa/clinical-trials&utm_campaign=Badge_Grade_Settings)

Set of parsers and classes for clinical trials data from [ClinicalTrials.gov](https://clinicaltrials.gov)

## Installation

```bash
pip install -e .  
```

## Usage

This package is mainly intended for working with clinical trials data dump in xml files.

```python
from CTnlp.parsers import parse_clinical_trials_from_folder

TRIALS_FOLDER = "PATH/TO/TRIALS/IN/XML/"
cts = parse_clinical_trials_from_folder(folder_name=TRIALS_FOLDER)
```

`cts` will be a list of `ClinicalTrials` objects.


In order to convert clinical trials to dictionary you can use `todict` method from `dataclasses`:

```python
from dataclasses import asdict

[asdict(ct) for ct in cts]
```

## Data

To download data for your analysis, follow the description from [here](https://clinicaltrials.gov/ct2/resources/download#DownloadAllData).

Description of the ClinicalTrials schema: <https://prsinfo.clinicaltrials.gov/ProtocolRecordSchema.xsd>
