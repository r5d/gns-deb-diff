# Copyright 2013 rsiddharth <rsiddharth@ninthfloor.org>
#
# This work is free. You can redistribute it and/or modify it under
# the terms of the Do What The Fuck You Want To Public License,
# Version 2, as published by Sam Hocevar. See the COPYING file or
# <http://www.wtfpl.net/> for more details.

import subprocess as child
import shlex

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
    local_dir =  raw_input(">> local directory to store bzr branch: ").strip()

    # absolute path to file which contains the packages names.
    # one package per line.
    stdin = raw_input(">> packages list file (absolute path): ").strip()

    if (len(stdin) != 0):
        pkgs_file = stdin
    else:
        pkgs_file = "packages-parkes.list"

    packages_list = get_packages()

    return packages_list


def read_gns_readme(package):
    """
    Reads & returns the README.gNewSense file for the package.

    If the README.gNewSense is not present, it returns None.
    """

    global local_dir

    try:
        readme_file = open("%s/%s/debian/README.gNewSense" % (local_dir,
                                                              package),
                           'r')
    except IOError, e:
        print "Trouble opening %s/%s"  % (local_dir, package)
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

pkgs_list = get_paraphernalia()
deploy_packages_locally(pkgs_list)
pkg_readmes, noreadme_pkgs = slurp_readmes(pkgs_list)
