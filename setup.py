#!/usr/bin/env python

import setuptools

name = 'HBlib'


setuptools.setup(
    name=name,
    version='0.1',
    author="Tyler Jachetta",
    author_email="me@tylerjachetta.net",
    url="tylerjachetta.net",
    description="Miscelaneous puppet libraries and utilities",
    long_description="todo",
    install_requires=['PyYAML'],
    license="GPG version 3",
    packages=setuptools.find_packages(),
    data_files=[],
    entry_points={
        'console_scripts': [],
    }
)
