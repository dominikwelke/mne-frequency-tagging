"""
mne-frequency-tagging
analyze electrophysiological data from frequency tagging experiments using mne-python

Author: Dominik Welke <dominik.welke@web.de>
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mne-frequency-tagging",
    version="0.1",
    author="Dominik Welke",
    author_email="dominik.welke@web.de",
    description="analyzing electrophysiological data from frequency tagging experiments using mne-python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dominikwelke/mne-frequency-tagging",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
