"""Setup configuration for DriftLab."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="driftlab",
    version="0.1.0",
    author="DriftLab Team",
    description="Production-grade ML monitoring toolkit for drift detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "evidently>=0.4.0",
        "pyyaml>=5.4.0",
        "sentence-transformers>=2.2.0",
    ],
    entry_points={
        "console_scripts": [
            "driftlab=driftlab.cli:main",
        ],
    },
)

