#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of gns-deb-diff.
#
#  gns-deb-diff is under the Public Domain. See
#  <https://creativecommons.org/publicdomain/zero/1.0>

import os
import shlex
import sys

from os import path
from subprocess import run, PIPE


# list of recognized fields.
field_list = [
    "Change-Type",
    "Changed-From-Debian",
]

# bzr
bzr_base_url = 'bzr://bzr.savannah.gnu.org/gnewsense/'
readme_url_fmt = '%s/packages-{}/{}/debian/README.gNewSense' % bzr_base_url


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


def execute(cmd, out=None, err=None):
    """Run `cmd`. Returns an instance of `subprocess.CompletedProcess`

    `cmd` must be a string containing the command to run.
    """
    cmd = shlex.split(cmd)

    try:
        completed_process = run(cmd, stdout=out, stderr=err)
    except (FileNotFoundError, OSError, ValueError) as e:
        print("Error running '%s'\n Error Info:\n %r" % (cmd[0], e),
              file=sys.stderr)
        sys.exit(1)

    return completed_process


def get_packages(pkgs_file):
    """Return an iterator contaning of package names from `pkgs_file`.

    """
    pkgs = read_file(pkgs_file).split('\n')
    # sanitize
    pkgs_iter = map(lambda x: x.strip(), pkgs)

    return pkgs_iter


def save_gns_readme(content, release, pkg, local_dir):
    """Save README.gNewsense locally.

    :param str content:
        Content of the README.gNewsense file.
    :param str release:
        Release name.
    :param str pkg:
        Package name.
    :param str local_dir:
        Root directory under which readme of all packages get stored.
    """
    # create gns_readme dir. for pkg.
    gns_readme_dir = path.join(local_dir, release, pkg, 'debian')

    try:
        os.makedirs(gns_readme_dir, exist_ok=True)
    except Exception as e:
        print("Error creating directory '%s'\n Error Info:\n %r" % (gns_readme_dir, e),
              file=sys.stderr)
        sys.exit(1)

    gns_readme = path.join(gns_readme_dir, 'README.gNewSense')

    with open(gns_readme, 'wb') as f:
        f.write(content)
        f.flush()
        print('Saved {}'.format(gns_readme))


def slurp_gns_readme(release, pkg, local_dir):
    """Read and save the README.gNewSense for `pkg` in `release`.

    The README.gNewSense file gets save at `local_dir`/`release`/`pkg`/debian/
    """
    readme_url = readme_url_fmt.format(release, pkg)
    cmd = 'bzr cat {}'.format(readme_url)
    cp = execute(cmd, out=PIPE, err=PIPE)

    if(cp.returncode == 0):
        save_gns_readme(cp.stdout, release, pkg, local_dir)
        return True
    else:
        print("README.gNewSense not found for package {}".format(pkg),
              file=sys.stderr)
        return False
