from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pthat",
    version="1.0.1",
    packages=find_packages(exclude=("tests", "examples")),
    python_requires='>=3.6',
)
