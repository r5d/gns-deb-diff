#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of gns-deb-diff.
#
#  gns-deb-diff is under the Public Domain. See
#  <https://creativecommons.org/publicdomain/zero/1.0>

import json
import os
import re
import shlex
import sys

import requests

from os import path
from subprocess import run, PIPE

from bs4 import BeautifulSoup

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


def write_file(fpath, content):
    """Write `content` to file `fpath`.

    """
    try:
      f = open(fpath, 'w')
      f.write(content)
      f.close()
    except IOError as e:
        print('Error creating and writing content to {}\n {}'.format(
            fpath, e))
        exit(1)


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


def read_packages(pkgs_file):
    """Return an iterator contaning of package names from `pkgs_file`.

    """
    pkgs = read_file(pkgs_file).split('\n')
    # sanitize
    pkgs_iter = map(lambda x: x.strip(), pkgs)

    return pkgs_iter


def get_packages(release):
    """Return newline separated list of packages for `release`.

    List of packages is slurped from
        http://bzr.savannah.gnu.org/lh/gnewsense/packages-`release`
    """
    url = 'http://bzr.savannah.gnu.org/lh/gnewsense/packages-{}/'
    req = url.format(release)

    try:
        res = requests.get(req)
    except ConnectionError as ce:
        print('ERROR: Problem GETting {} \n{}'.format(req, ce))
        sys.exit(1)

    if res.status_code != 200:
        print('{}: Error GETting {}'.format(res.status_code, req))
        sys.exit(1)

    html_forest = BeautifulSoup(res.text, 'html.parser')

    pkgs = '' # newline separated list of pkgs.
    for td in html_forest.find_all('td', class_='autcell'):
        pkgs += td.a.string.strip() + '\n'

    return pkgs


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
        print("Error creating directory '%s'\n Error Info:\n %r" %
              (gns_readme_dir, e), file=sys.stderr)
        sys.exit(1)

    gns_readme = path.join(gns_readme_dir, 'README.gNewSense')
    write_file(gns_readme, content)
    print('Saved {}'.format(gns_readme))


def slurp_gns_readme(release, pkg, local_dir):
    """Read and save the README.gNewSense for `pkg` in `release`.

    The README.gNewSense file gets save at `local_dir`/`release`/`pkg`/debian/
    """
    readme_url = readme_url_fmt.format(release, pkg)
    cmd = 'bzr cat {}'.format(readme_url)
    cp = execute(cmd, out=PIPE, err=PIPE)

    if(cp.returncode == 0):
        save_gns_readme(cp.stdout.decode(), release, pkg, local_dir)
        return True
    else:
        print("README.gNewSense not found for package {}".format(pkg),
              file=sys.stderr)
        return False


def slurp_all_gns_readmes(release, pkgs, local_dir):
    """Read and save all README.gNewSense for `pkgs` in `release`.

    The README.gNewSense files gets saved under `local_dir`/`release`

    Returns list of packages in `pkgs` that does not have README.gNewSense.
    """
    pkgs_noreadmes = []
    for pkg in pkgs:
        slurped = slurp_gns_readme(release, pkg, local_dir)

        if(not slurped):
            pkgs_noreadmes.append(pkg)

    return pkgs_noreadmes


def read_gns_readme(release, pkg, local_dir):
    """Returns content of README.gNewSense for `pkg`.

    If `README.gNewSense` does not exists for `pkg`, None is returned.

    """
    readme_path = path.join(local_dir, release, pkg, 'debian',
                            'README.gNewSense')
    readme_content = read_file(readme_path)

    return readme_content


def slurp_fields_from_readme(content):
    """Returns dict containing fields slurped from `content`

    - If a field is not defined or if its value is empty in the
    `content`, then its corresponding value in the dict will be None.

    """
    field_values = {}
    for field in field_list:
        pattern = r'{}:[ ]*(.+)'.format(field)
        field_pattern = re.compile(pattern)
        field_match = field_pattern.search(content)

        if (field_match and
            field_match.group(1) and
            field_match.group(1).strip()):
            field_values[field] = field_match.group(1).strip()
        else:
            field_values[field] = None

    return field_values


def config_dir():
    """Return the gns-deb-diff config directory.

    As a side effect, the directory is created if it does not exist.

    """
    cd = os.path.join(os.getenv('HOME'), '.config', 'gns-deb-diff')

    if not os.path.isdir(cd):
        os.makedirs(cd)

    return cd


def config_file():
    return os.path.join(config_dir(), 'config')


def read_config_file():
    """Return config as a Python Object; False when config does not \
    exist.

    """
    cf = config_file()

    if not os.path.isfile(cf):
        return False

    return json.load(open(cf, 'r'))


def pkgs_dir():
    """Return the `pkgs` directory.

    As a side effect, the directory is created if it does not exist.
    """
    pd = os.path.join(config_dir(), 'pkgs')
    if not os.path.isdir(pd):
        os.mkdir(pd)

    return pd


def mk_pkgs_list(release):
    """Get pkgs for release and write to disk.

    It gets written to `~/.config/pkgs/release`.

    """
    pkgs = get_packages(release)
    pkgs_file = os.path.join(pkgs_dir(), release)
    write_file(pkgs_file, pkgs)


def readmes_dir(release):
    """Return readmes directory for `release`.

    As a side effect, the directory is created if it does not exist.
    """
    rd = os.path.join(config_dir(), 'readmes')
    if not os.path.isdir(rd):
        os.mkdir(rd)

    rd_release = os.path.join(rd, release)
    if not os.path.isdir(rd_release):
        os.mkdir(rd_release)

    return rd_release


def wiki_page_dir(release):
    """Get wiki page directory for `release`.
    """
    wd = os.path.join(config_dir(), 'wiki-page')

    if not os.path.isdir(wd):
        os.mkdir(wd)

    wd_release = os.path.join(wd, release)
    if not os.path.isdir(wd_release):
        os.mkdir(wd_release)

    return wd_release


def write_wiki_page(release, content):
    """Write wiki page `content` to `release`' last.rev file.

    """
    wd_release = wiki_page_dir(release)
    wp_file = os.path.join(wd_release, 'last.rev')
    write_file(wp_file, content)


def configured_p():
    """Returns True if gns-deb-diff is configured; False otherwise.
    """
    if os.path.isfile(config_file()):
        return True
    else:
        return False


def configure():
    """Configure gns-deb-diff.
    """
    # prompt username and password.
    config = {}
    config['user'] = input('gNewSense wiki username: ')
    config['pass'] = input('gNewSense wiki password: ')

    json.dump(config, open(config_file(), 'w'))
    os.chmod(config_file(), mode=0o600)
