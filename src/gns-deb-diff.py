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
from sys import exit

# global variables.
bzr_base_url = ""
local_dir = ""
pkgs_file = ""

def get_packages():
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

    print packages

    return packages


def bzr_branch_command(package):
    """
    Return the command to create a local bzr branch of package.
    """
    global bzr_base_url, local_dir

    return "bzr branch %s/%s %s/%s" % (bzr_base_url, package,
                                       local_dir, package)

def fetch_bzr_branch(package):
    """
    Create a local bzr branch of the package.
    """
    bzr_branch_cmd = bzr_branch_command(package)
    print "doing %s ..." % bzr_branch_cmd
    return child.call(shlex.split(bzr_branch_cmd))


def deploy_packages_locally(packages_list):
    """
    Create a local bzr branch for each package in packages list.
    """
    for pkg in packages_list:
        fetch_bzr_branch(pkg)

def get_paraphernalia():
    """
    Read relevant values from stdin to start work.
    """
    global bzr_base_url, local_dir, pkgs_file

    stdin = raw_input(">> remote bzr url: ").strip()

    if (len(stdin) != 0):
        bzr_base_url = stdin
    else:
        bzr_base_url = "bzr://bzr.savannah.gnu.org/gnewsense/packages-parkes"

    # directory under which the bzr branches has to be stored.
    stdin =  raw_input(">> local directory to store bzr branches: ").strip()

    if (len(stdin) !=0):
        local_dir = path.abspath(stdin)
    else:
        local_dir = path.expanduser("~/gnewsense/packages-parkes")

    if not path.isdir(local_dir):
        try:
            os.makedirs(local_dir)
        except OSError, e:
            print "ERROR: Unable to create %s directory" % local_dir
            exit(1)


    # packages list file should contain package names listed one per
    # line.
    stdin = raw_input(">> packages list file: ").strip()

    if (len(stdin) != 0):
        pkgs_file = path.abspath(stdin)
    else:
        pkgs_file = path.abspath("packages-parkes.list")

    packages_list = get_packages_list()

    return packages_list


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
        print e
        return None # give up!

    readme_content = readme_file.read().strip()
    readme_file.close()

    return readme_content


def slurp_readmes(package_list):
    """Reads the README.gNewSense for each package in package_list.

    The readme content of all packages is put into a dict.
    """

    pkg_readmes = {}
    noreadme_pkgs = []

    for pkg in package_list:
        readme_content = read_gns_readme(pkg)

        if readme_content is not None:
            pkg_readmes[pkg] = readme_content
        else:
            noreadme_pkgs.append(pkg)

    return pkg_readmes, noreadme_pkgs


def generate_diff_table(pkg_readmes):
    """Generates the gNewSense Debian Diff table in MoinMoin syntax and \
returns it as a string.
    """

    table = [
        "||Package||Difference||",
        ]

    for pkg, diff in pkg_readmes.items():
        row = "||%s||%s||" % (pkg, diff)
        table.append(row)

    return table


def write_diff_table(table, filepath):
    """Write the table to file."""

    try:
        table_file = open(filepath, 'w')

        for row in table:
            table_file.write("%s\n" % row)

    except IOError, e:
        print "Something went wrong: %r" % e
    finally:
        table_file.close()


def do_magic():
    """
    Does what it has to do :)
    """
    pkgs_list = get_paraphernalia()
    deploy_packages_locally(pkgs_list)
    pkg_readmes, noreadme_pkgs = slurp_readmes(pkgs_list)
    diff_table = generate_diff_table(pkg_readmes)
    write_diff_table(diff_table, "gns-deb-diff-table.txt")

    print "README.gNewSense not found for: %s" % noreadme_pkgs

do_magic()
