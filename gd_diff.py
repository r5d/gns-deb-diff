#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of gns-deb-diff.
#
#  gns-deb-diff is under the Public Domain. See
#  <https://creativecommons.org/publicdomain/zero/1.0>

import sys

# list of recognized fields.
field_list = [
    "Change-Type",
    "Changed-From-Debian",
]

def read_file(fpath):
    """Read file `f` and return its content.

    """
    try:
        f = open(fpath, 'r')
    except FileNotFoundError as e:
        print("Error opening '%s' \n Error Info:\n  %r" % (fpath, e),
              file=sys.stderr)
        sys.exit(1)

    return f.read()


def get_packages(pkgs_file):
    """Return an iterator contaning of package names from `pkgs_file`.

    """
    pkgs = read_file(pkgs_file).split('\n')
    # sanitize
    pkgs_iter = map(lambda x: x.strip(), pkgs)

    return pkgs_iter
