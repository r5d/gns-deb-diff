# Copyright 2013 rsiddharth <rsiddharth@ninthfloor.org>
#
# This work is free. You can redistribute it and/or modify it under
# the terms of the Do What The Fuck You Want To Public License,
# Version 2, as published by Sam Hocevar. See the COPYING file or
# <http://www.wtfpl.net/> for more details.

import subprocess as child
import shlex
import os.path as path
import os
import re
from sys import exit, argv
import gns_wiki as wiki

# global variables.
bzr_base_url = None
local_dir = None
pkgs_file = None
src_dir = None

# list of recognized fields.
field_list = [
    "Change-Type",
    "Changed-From-Debian",
    ]

def get_packages_list():
    """
    Return a list of package names from pkgs_file.
    """
    global pkgs_file

    try:
        packages_file = open(pkgs_file, 'r')
    except IOError, e:
        print "Trouble opening %r" % pkgs_file
        print e
        return None

    packages = []
    for package in packages_file.readlines():
        packages.append(package.strip())

    packages_file.close()

    return packages


def mirror_bzr_branch(package):
    """
    Create/update a local bzr branch of the package from remote branch.
    """
    global bzr_base_url, local_dir

    local_pkg_dir = path.join(local_dir,package)

    if path.exists(local_pkg_dir):
        current_dir = os.getcwd()
        os.chdir(local_pkg_dir)

        command = "bzr pull %s/%s" % (bzr_base_url,
                                      package)
        returncode = child.call(shlex.split(command))

        # back to current dir
        os.chdir(current_dir)
    else:
        # package doesn't exists so locally create one.
        command = "bzr branch %s/%s %s" % (bzr_base_url, package,
                                              local_pkg_dir)

        returncode = child.call(shlex.split(command))

    return returncode

def get_packages(packages_list):
    """
    Create/update a local bzr branch for each package in packages list.
    """
    for pkg in packages_list:
        code = mirror_bzr_branch(pkg)

        assert code == 0, "bzr branch mirroring for %s FAILED" % pkg

def process_input():
    """
    Read relevant values from argv to start work.
    """
    global bzr_base_url, local_dir, pkgs_file, src_dir

    # defaults
    remote_bzr_url = "bzr://bzr.savannah.gnu.org/gnewsense/packages-parkes"
    local_packages_directory = "~/gnewsense/packages-parkes"

    src_dir = path.dirname(argv[0])

    try:
        pkgs_file = argv[1]
    except IndexError:
        print "format: python path/to/gns-deb-diff.py \
packages-list-file local-packages-directory remote-bzr-url\
\n\n`local-packages-directory' & 'remote-bzr-url' are \
optional\ndefault values:\n\tlocal-packages-directory: %s\n\t\
remote-bzr-url: %s" % (remote_bzr_url, local_packages_directory)
        exit(1)


    # check if the local-packages-directory is given
    if (len(argv) > 2):
        local_dir = path.abspath(argv[2])
    else:
        # stick with default directory
        local_dir = path.expanduser(local_packages_directory)

    if not path.isdir(local_dir):
        try:
            os.makedirs(local_dir)
        except OSError:
            print "ERROR: Unable to create %s directory" % local_dir
            exit(1)

    # check if remote_bzr_url is given
    if (len(argv) > 3):
        bzr_base_url = argv[3]
    else:
        # stick with default url
        bzr_base_url = remote_bzr_url


def read_gns_readme(package):
    """
    Reads & returns the README.gNewSense file for the package.

    If the README.gNewSense is not present, it returns None.
    """

    global local_dir

    readme_file_path = path.join(local_dir, package,
    "debian/README.gNewSense")

    try:
        readme_file = open(readme_file_path, 'r')
    except IOError, e:
        # README.gNewSense file not found.
        return None # give up!

    readme_content = readme_file.read().strip()
    readme_file.close()

    return readme_content

def generate_tuple(package, readme_content):
    """Generates a tuple of the diff table.

    Keyword arguments:
    package -- name of package
    readme_content -- content of the README.gNewSense for this package.


    Returns a dict of the form {'pkg': package_name, 'Change-Type':
    "Added/Removed/Modified", 'Changed-From-Debian': 'one line
    description'}

    The value for keys `Change-Type' & `Changed-Frome-Debian' is None,
    if values for those are not present in the README.gNewSense.
    """

    global field_list

    pkg_tuple = {"pkg": package}

    for field in field_list:
        pattern = r"%s:\s*(.+)" % field
        field_pattern = re.compile(pattern)
        field_match = field_pattern.search(readme_content)

        if not field_match is None:
            field_value = field_match.group(1)
            pkg_tuple[field] = field_value
        else:
            # This field is not present in the README, so:
            pkg_tuple[field] = None

    return pkg_tuple


def slurp_readmes(package_list):
    """Reads the README.gNewSense for each package in package_list \
and generates tuples for each package.

    Packages which doesn't have a README.gNewSense file is put in a
    seperate list.

    The function returns the tuple dict and a list of packages (if
    any), that doesn't have README.gNewSense file.
    """

    pkg_tuples = [] # will hold a list of dicts
    noreadme_pkgs = []

    for pkg in package_list:
        readme_content = read_gns_readme(pkg)

        if readme_content is not None:
            pkg_tuple = generate_tuple(pkg, readme_content)
            pkg_tuples.append(pkg_tuple)
        else:
            noreadme_pkgs.append(pkg)

    return pkg_tuples, noreadme_pkgs


def generate_diff_table(pkg_tuples):
    """Generates the gNewSense Debian Diff table in MoinMoin syntax and \
returns it as a string.

    """

    global field_list

    table = [
        "||'''Source Package'''||'''Change Type'''||'''Reason'''||\
'''More Info'''||",
        ]

    for pkg_tuple in pkg_tuples:
        # get package name first:
        pkg_name = pkg_tuple["pkg"]

        more_info_link = "http://bzr.savannah.gnu.org/lh/gnewsense/\
packages-parkes/%s/annotate/head:/debian/README.gNewSense" % pkg_name

        # start constructing a row for this package:
        row = "||%s" % pkg_name

        # add the `change type' & `reason' cells to row
        for field in field_list:
            field_value = pkg_tuple[field]

            if field_value is None:
                # insert a blank cell
                row += "|| "
            else:
                # insert the field value
                row += "||%s" % field_value

        # added `more info link' in another cell
        row += "||[[%s|more info]]||" % more_info_link

        table.append(row)

    return table

def do_magic():
    """
    Does what it has to do :)
    """

    global src_dir

    process_input()
    pkgs_list = get_packages_list()
    get_packages(pkgs_list)
    pkg_tuples, noreadme_pkgs = slurp_readmes(pkgs_list)
    diff_table = generate_diff_table(pkg_tuples)
    wiki.update(diff_table, src_dir)

    if(len(noreadme_pkgs) != 0):
        print "README.gNewSense not found for: %s" % noreadme_pkgs

do_magic()
