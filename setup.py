#!/usr/bin/env python3

import setuptools
import os


def readme():
    this_directory = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        return f.read()


setuptools.setup(
    name="app_executor",
    version='1.0.3',
    author="Mariusz Pasek",
    author_email="pasiasty@gmail.com",
    description="Tool for safe launching external processes",
    entry_points={"pytest11": ["app_executor = app_executor.conftest"]},
    url="https://github.com/pasiasty/app-executor",
    packages=setuptools.find_packages(),
    install_requires=['pytest'],
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
