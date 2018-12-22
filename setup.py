#!/usr/bin/env python

import setuptools

name = 'hb_lib'


setuptools.setup(
    name=name,
    version='0.2',
    author="Tyler Jachetta",
    author_email="me@tylerjachetta.net",
    url="tylerjachetta.net",
    description="Miscelaneous puppet libraries and utilities",
    long_description="todo",
    requires=['pyyaml'],
    license="GPG version 3",
    packages=setuptools.find_packages(),
    data_files=[],
    entry_points={
        'console_scripts': [],
    }
)
