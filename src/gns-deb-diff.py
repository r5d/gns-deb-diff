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
from sys import exit, argv

# global variables.
bzr_base_url = None
local_dir = None
pkgs_file = None
table_file = None

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
    global bzr_base_url, local_dir, pkgs_file, table_file

    # defaults
    remote_bzr_url = "bzr://bzr.savannah.gnu.org/gnewsense/packages-parkes"
    local_packages_directory = "~/gnewsense/packages-parkes"

    try:
        pkgs_file = argv[1]
        table_file = argv[2]
    except IndexError:
        print "format: python path/to/gns-deb-diff.py \
packages-list-file output-table-file local-packages-directory \
remote-bzr-url\n\n`local-packages-directory' & 'remote-bzr-url' are \
optional\ndefault values:\n\tlocal-packages-directory: %s\n\t\
remote-bzr-url: %s" % (remote_bzr_url, local_packages_directory)
        exit(1)


    # check if the local-packages-directory is given
    if (len(argv) > 3):
        local_dir = path.abspath(argv[3])
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
    if (len(argv) > 4):
        bzr_base_url = argv[4]
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
        print e
        return None # give up!

    readme_content = readme_file.read().strip()
    readme_file.close()

    return readme_content


def slurp_readmes(package_list):
    """Reads the README.gNewSense for each package in package_list.

    The README content of all packages is put into a dict. Packages
    which doesn't have a README.gNewSense file is put in a seperate
    list.
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

    The generated output is *not* clean since the content under the
    Difference column often has newlines, which MoinMoin doesn't allow
    inside a table.

    So, you might have to manually clean the table before putting it
    on the gNewSense Wiki.
    """

    table = [
        "||'''Package'''||'''Difference'''||",
        ]

    for pkg, diff in pkg_readmes.items():
        row = "||%s||%s||" % (pkg, diff)
        table.append(row)

    return table


def write_diff_table(table):
    """Write the table to file.

    The filename is read from stdin
    """
    global table_file

    try:
        output_file = open(table_file, 'w')

        for row in table:
            output_file.write("%s\n" % row)

    except IOError, e:
        print "Something went wrong: %r" % e
    finally:
        output_file.close()


def do_magic():
    """
    Does what it has to do :)
    """

    global table_file

    process_input()
    pkgs_list = get_packages_list()
    get_packages(pkgs_list)
    pkg_readmes, noreadme_pkgs = slurp_readmes(pkgs_list)
    diff_table = generate_diff_table(pkg_readmes)
    write_diff_table(diff_table)

    print "README.gNewSense not found for: %s" % noreadme_pkgs

do_magic()
