#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of gns-deb-diff.
#
#  gns-deb-diff is under the Public Domain. See
#  <https://creativecommons.org/publicdomain/zero/1.0>

import argparse
import json
import os
import re
import shlex
import sys
import xmlrpc.client

import requests

from os import path
from subprocess import run, PIPE
from urllib.parse import urljoin
from xmlrpc.client import ServerProxy, MultiCall, Fault

from bs4 import BeautifulSoup
from pkg_resources import resource_string

from gns_deb_diff._version import __version__

# list of recognized fields.
field_list = [
    'Change-Type',
    'Changed-From-Debian',
]

# urls
sv_bzr_http = 'http://bzr.savannah.gnu.org'
sv_bzr_gns = '/'.join(['bzr://bzr.savannah.gnu.org', 'gnewsense'])
gns_wiki = 'http://gnewsense.org'

# fmt
readme_link_fmt = '/'.join([sv_bzr_http, 'lh', 'gnewsense',
                            'packages-{}', '{}', 'annotate',
                            'head:', 'debian', 'README.gNewSense'])
readme_url_fmt = '/'.join([sv_bzr_gns, 'packages-{}', '{}','debian',
                           'README.gNewSense'])


def read_file(fpath):
    """Read file `f` and return its content.

    """
    try:
        f = open(fpath, 'r')
    except FileNotFoundError as e:
        print('Error opening \'{}\' \n Error Info:\n  {}'.format(fpath, e),
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
    """Return list contaning of package names from `pkgs_file`.

    """
    pkgs = read_file(pkgs_file).split('\n')
    # sanitize
    pkgs_iter = map(lambda x: x.strip(), pkgs)

    return list(pkgs_iter)


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

    return pkgs_file


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


def wiki_page_path(release):
    """Returns the path to file that contains wiki page for `release`.

    """
    wd_release = wiki_page_dir(release)
    return os.path.join(wd_release, 'wiki.page')


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


def save_gns_readme(content, release, pkg):
    """Save README.gNewsense locally.

    :param str content:
        Content of the README.gNewsense file.
    :param str release:
        Release name.
    :param str pkg:
        Package name.
    """
    # create gns_readme dir. for pkg.
    gns_readme_dir = path.join(readmes_dir(release), pkg, 'debian')

    try:
        os.makedirs(gns_readme_dir, exist_ok=True)
    except Exception as e:
        print("Error creating directory '%s'\n Error Info:\n %r" %
              (gns_readme_dir, e), file=sys.stderr)
        sys.exit(1)

    gns_readme = path.join(gns_readme_dir, 'README.gNewSense')
    write_file(gns_readme, content)
    print('Saved {}'.format(gns_readme))


def slurp_gns_readme(release, pkg):
    """Read and save the README.gNewSense for `pkg` in `release`.

    """
    readme_url = readme_url_fmt.format(release, pkg)
    cmd = 'bzr cat {}'.format(readme_url)
    cp = execute(cmd, out=PIPE, err=PIPE)

    if(cp.returncode == 0):
        save_gns_readme(cp.stdout.decode(), release, pkg)
        return True
    else:
        print("README.gNewSense not found for package {}".format(pkg),
              file=sys.stderr)
        return False


def slurp_all_gns_readmes(release, pkgs):
    """Read and save all README.gNewSense for `pkgs` in `release`.

    Returns list of packages in `pkgs` that does not have README.gNewSense.
    """
    pkgs_noreadmes = []
    for pkg in pkgs:
        slurped = slurp_gns_readme(release, pkg)

        if(not slurped):
            pkgs_noreadmes.append(pkg)

    return pkgs_noreadmes


def read_gns_readme(release, pkg):
    """Returns content of README.gNewSense for `pkg`.

    If `README.gNewSense` does not exists for `pkg`, None is returned.

    """
    readme_path = path.join(readmes_dir(release), pkg, 'debian',
                            'README.gNewSense')

    if not path.isfile(readme_path):
        return None

    readme_content = read_file(readme_path)
    return readme_content


def slurp_fields_from_readme(content):
    """Returns dict containing fields slurped from `content`.

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


def get_wiki_page_data(release):
    """Returns data needed to generate the gNewSense Debian Diff table.

    """
    # get packages for release.
    pkgs_file = mk_pkgs_list(release)
    pkgs = read_packages(pkgs_file)

    # get readmes for release.
    pkgs_noreadmes = slurp_all_gns_readmes(release, pkgs)

    # go through each pkg's readme and slurp the fields.
    table_data = {}
    for pkg in pkgs:
        readme_content = read_gns_readme(release, pkg)
        if readme_content:
            table_data[pkg] = slurp_fields_from_readme(readme_content)

    return pkgs_noreadmes, table_data


def construct_table_row(release, pkg, change, reason):
    """Return a table row in moinmoin wiki markup.

    """
    if change is None:
        change = ' '
    if reason is None:
        reason = ' '

    more_info_link = readme_link_fmt.format(release, pkg)

    return '||{}||{}||{}||[[{}|more_info]]||'.format(pkg, change, reason,
                                                   more_info_link)


def generate_wiki_table(release):
    """Generate and return the gNewSense Debian Diff table as a string.
    """
    pkgs_noreadmes, table_data = get_wiki_page_data(release)

    wiki_table = ''
    for pkg, fields in table_data.items():
        change = fields['Change-Type']
        reason = fields['Changed-From-Debian']
        wiki_table += construct_table_row(release, pkg, change, reason) + '\n'

    return pkgs_noreadmes, wiki_table


def gns_wiki_header():
    """Return gNewSense wiki header."""
    header = resource_string(__name__, 'gns_deb_diff/data/wiki-header.txt')
    return header.decode()


def generate_wiki_page(release):
    """Generate and return the gNewSense Debian Diff wiki page.
    """
    pkgs_noreadmes, wiki_table = generate_wiki_table(release)
    wiki_page = gns_wiki_header() + '\n' + wiki_table

    return pkgs_noreadmes, wiki_page


def read_wiki_page(release):
    """Read wiki page for `release` from disk.
    """
    wp_file = wiki_page_path(release)

    if not path.isfile(wp_file):
        return None

    return read_file(wp_file)


def write_wiki_page(release, content):
    """Write wiki page `content` to `release`' last.rev file.

    """
    wp_file = wiki_page_path(release)
    write_file(wp_file, content)


def get_wiki_mc(url, user, passwd): # pragma: no cover
    """Return instance of `xmlprc.client.MultiCall` object.

    """
    url = urljoin(url, '?action=xmlrpc2')
    conn = ServerProxy(url, allow_none=True)

    try:
        token = conn.getAuthToken(user, passwd)
    except Fault as f:
        print(f.faultString)
        exit(1)

    mc = MultiCall(conn)
    mc.applyAuthToken(token)

    return mc


def push_wiki_page(url, user, passwd, version, content):
    """Push `release`' wiki page to wiki at `uri`.

    """
    def process_result(r, f=None):
        if(r == 'SUCCESS'):
            print('auth success.')
        elif(r == True):
            print('wiki page updated.')
        elif(f and f.faultCode == 'INVALID'):
            print('auth failure')
        elif(f and f.faultCode == 1):
            print('wiki page not updated.')


    page = '/'.join(['Documentation', str(version), 'DifferencesWithDebian'])
    mc = get_wiki_mc(url, user, passwd)
    mc.putPage(page, content)

    results = mc()
    try:
        for r in results:
            process_result(r)
    except Fault as f:
        process_result(None, f)


def make_push(args):
    """make wiki page and push it.
    """
    release = args.release
    version = args.version

    # read previously generated wiki page for release
    old_wiki_page = read_wiki_page(release)

    # freshly generate wiki page
    pkgs_noreadmes, wiki_page = generate_wiki_page(release)

    if old_wiki_page == wiki_page:
        print('no changes.')
        return

    # configure if needed.
    if not configured_p():
        configure()

    # read configuration.
    config = read_config_file()

    write_wiki_page(release, wiki_page)
    push_wiki_page(gns_wiki, config['user'], config['pass'], version, wiki_page)

    return config, pkgs_noreadmes, old_wiki_page, wiki_page


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('release', help='gNewSense release name')
    parser.add_argument('version', help='gNewSense version number',
                        type=int)

    return parser.parse_args()


def main():
    args = get_args()
    make_push(args)

