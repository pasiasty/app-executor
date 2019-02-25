#!/usr/bin/env python3

import setuptools
import os


def dependencies():
    requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
    return open(requirements_path, 'r').read().splitlines()


def readme():
    with open(os.path.join(os.getcwd(), 'README.md')) as f:
        return f.read()


setuptools.setup(
    name="app_executor",
    version='1.0.0',
    author="Mariusz Pasek",
    author_email="pasiasty@gmail.com",
    description="Tool for safe launching external processes",
    entry_points={"pytest11": ["app_executor = app_executor.conftest"]},
    url="EMPTY",
    packages=setuptools.find_packages(),
    install_requires=dependencies(),
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
