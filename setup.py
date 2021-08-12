#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="preproc_chip_like_data",
    version="0.1.0",
    author="Hanbin Lu",
    author_email="lhb032@gmail.com",
    license="LICENSE",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    scripts=["scripts/sra_chip_to_bw.py", "scripts/tagdir_to_bw.py"],
)
