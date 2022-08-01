from setuptools import find_packages, setup

setup(
    name="CTnlp",
    packages=find_packages(),
    description="Library for parsing ClinicalTrials.gov data.",
    version="0.0.1",
    author="Wojciech Kusa",
    author_email="wojciech.kusa@tuwien.ac.at",
    install_requires=["tqdm==4.64.0", "defusedxml==0.7.1"],
    license="GPL-3.0",
)
