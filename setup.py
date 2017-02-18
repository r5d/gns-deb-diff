#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of gns-deb-diff.
#
#  gns-deb-diff is under the Public Domain. See
#  <https://creativecommons.org/publicdomain/zero/1.0>

"""
gns-deb-diff setup.
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

from gns_deb_diff._version import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

config = {
    'name': 'gns-deb-diff',
    'version': __version__,
    'description': 'Documents difference between gNewsSense and Debian.',
    'long_description': long_description,
    'url': 'https://git.ricketyspace.net/gns-deb-diff',
    'author': 'rsiddharth',
    'author_email': 'rsiddharth@ninthfloor.org',
    'license': 'Public Domain',
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: General',
    ],
    'keywords': 'gNewSense Debian documentation',
    'py_modules': ['gd_diff'],
    'packages': ['gns_deb_diff'],
    'include_package_data': True,
    'install_requires': ['beautifulsoup4', 'requests'],
    'entry_points': {
        'console_scripts': ['gd-diff = gd_diff:main']
    },
}

setup(**config)
