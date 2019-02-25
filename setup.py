#!/usr/bin/env python3

import setuptools
import os


def dependencies():
    requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
    return open(requirements_path, 'r').read().splitlines()


setuptools.setup(
    name="app_executor",
    version='1.0.0',
    author="Mariusz Pasek",
    author_email="pasiasty@gmail.com",
    description="Tool for safe launching external processes",
    url="EMPTY",
    packages=setuptools.find_packages(),
    install_requires=dependencies(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
