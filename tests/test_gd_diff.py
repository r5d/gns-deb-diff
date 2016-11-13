#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of gns-deb-diff.
#
#  gns-deb-diff is under the Public Domain. See
#  <https://creativecommons.org/publicdomain/zero/1.0>

import os
import subprocess
import sys

from io import StringIO
from os import path
from shutil import rmtree
from unittest import mock

from nose.tools import *

from gd_diff import *


class TestGdDiff(object):

    def setup(self):
        """Setup method for this class."""
        self.pkgs_file = 'tests/files/parkes-pkgs.list'
        self.small_pkgs_file = 'tests/files/small-parkes-pkgs.list'
        self.pkgs_file_ne = 'tests/nonexistent-file.list'
        self.gns_pkgs_dir = 'tests/gns-pkgs'
        self.test_home = 'tests/HOME'
        self.test_w_file = os.path.join(self.test_home, 'w_file')

        self.stderr_orig = sys.stderr

        # make test home
        os.mkdir(self.test_home, mode=0o700)


    def test_read_file_success(self):
        f_content = read_file(self.pkgs_file)

        assert isinstance(f_content, str)
        assert_equal(len(f_content.split('\n')), 82)


    @raises(SystemExit)
    def test_read_file_error(self):
        with open(os.devnull, 'w') as sys.stderr:
            f_content = read_file(self.pkgs_file_ne)


    def test_write_file(self):
        content = 'One Goodbye\n Stealing Romance'
        write_file(self.test_w_file, content)

        assert read_file(self.test_w_file) == content


    def test_execute_success(self):
        cmd = 'python --version'
        cp = execute(cmd, out=subprocess.PIPE)

        assert cp.returncode == 0
        assert cp.stdout.split()[0] == b'Python'
        assert cp.stdout.split()[1].startswith(b'3.5')

    def test_execute_cmderror(self):
        cmd = 'bzr cat bzr://bzr.sv.gnu.org/gnewsense/packages-parkes/nonexistent-packages/debian/README.gNewSense'
        cp = execute(cmd, err=subprocess.PIPE)

        assert cp.returncode == 3
        assert cp.stderr.startswith(b'bzr: ERROR:')


    @raises(SystemExit)
    def test_execute_raise_exception(self):
        cmd = 'cornhole computers'
        with open(os.devnull, 'w') as sys.stderr:
            cp = execute(cmd)


    def test_read_packages(self):
        pkgs_iter = read_packages(self.pkgs_file)
        assert len(list(pkgs_iter)) == 82

    def test_read_packages_sanity(self):
        pkgs_iter = read_packages(self.pkgs_file)

        for pkg in pkgs_iter:
            assert not ' ' in pkg

    @raises(SystemExit)
    def test_get_packages_error(self):
        res = get_packages('foo_release')


    def test_get_packages(self):
        pkgs = get_packages('parkes')

        assert_equal(pkgs, ['antlr', 'apt', 'apt-setup', 'autoconf', 'autoconf2.59', 'autoconf2.64', 'bacula', 'base-files', 'base-installer', 'batik', 'cairomm', 'cdebootstrap', 'cfitsio3', 'choose-mirror', 'claws-mail', 'db4.6', 'db4.7', 'db4.8', 'debian-cd', 'debian-edu', 'debian-installer', 'debian-installer-launcher', 'debootstrap', 'desktop-base', 'doc-linux', 'doc-linux-hr', 'doc-linux-it', 'doc-linux-ja', 'doc-linux-pl', 'enscript', 'epiphany-browser', 'fop', 'freetype', 'galaxia', 'gdm3', 'glibmm2.4', 'gnewsense-archive-keyring', 'gnome-desktop', 'gtkmm2.4', 'icedove', 'iceweasel', 'kde4libs', 'kdebase', 'kdebase-workspace', 'kdenetwork', 'kernel-wedge', 'lensfun', 'liferea', 'lintian', 'linux-2.6', 'linux-kernel-di-amd64-2.6', 'linux-kernel-di-i386-2.6', 'linux-latest-2.6', 'live-build', 'live-config', 'meta-gnome2', 'mplayer', 'net-retriever', 'objcryst-fox', 'openbox-themes', 'openjdk-6', 'openoffice.org', 'pangomm', 'perl-tk', 'pkgsel', 'popularity-contest', 'psutils', 'python-apt', 'screenlets', 'sip4-qt3', 'software-center', 'tcl8.4', 'tcl8.5', 'texlive-extra', 'tk8.4', 'tk8.5', 'update-manager', 'vim', 'wmaker', 'xchat', 'xdm', 'xorg-server', 'xserver-xorg-video-siliconmotion', 'yeeloong-base'])


    def test_save_gns_readme(self):
        cmd = 'bzr cat bzr://bzr.sv.gnu.org/gnewsense/packages-parkes/antlr/debian/README.gNewSense'
        cp = execute(cmd, out=subprocess.PIPE)
        readme_content = cp.stdout.decode() # convert to str

        # save it
        save_gns_readme(readme_content, 'parkes', 'antlr', self.gns_pkgs_dir)

        gns_readme_file = path.join(self.gns_pkgs_dir, 'parkes', 'antlr', 'debian', 'README.gNewSense')
        with open(gns_readme_file, 'rb') as f:
            assert f.read() == b'Changed-From-Debian: Removed example with non-free files.\nChange-Type: Modified\n\nFor gNewSense, the non-free unicode.IDENTs files are *actually* removed (see\nalso README.source). See gNewSense bug #34218 for details.\n'


    def test_save_gns_readme_double(self):
        cmd = 'bzr cat bzr://bzr.sv.gnu.org/gnewsense/packages-parkes/antlr/debian/README.gNewSense'
        cp = execute(cmd, out=subprocess.PIPE)
        readme_content = cp.stdout.decode() # convert to str

        # save it twice
        save_gns_readme(readme_content, 'parkes', 'antlr', self.gns_pkgs_dir)
        save_gns_readme(readme_content, 'parkes', 'antlr', self.gns_pkgs_dir)

        gns_readme_file = path.join(self.gns_pkgs_dir, 'parkes', 'antlr', 'debian', 'README.gNewSense')
        with open(gns_readme_file, 'rb') as f:
            assert f.read() == b'Changed-From-Debian: Removed example with non-free files.\nChange-Type: Modified\n\nFor gNewSense, the non-free unicode.IDENTs files are *actually* removed (see\nalso README.source). See gNewSense bug #34218 for details.\n'

    @raises(SystemExit)
    def test_save_gns_readme_error(self):
        os.mkdir(self.gns_pkgs_dir, mode=0o500)

        # must error out
        readme_content = 'lorem ipsum'
        with open(os.devnull, 'w') as sys.stderr:
            save_gns_readme(readme_content, 'parkes', 'antlr', self.gns_pkgs_dir)


    def test_slurp_gns_readme_success(self):
        saved = slurp_gns_readme('parkes', 'antlr', self.gns_pkgs_dir)
        assert saved == True

        gns_readme_file = path.join(self.gns_pkgs_dir, 'parkes',
                                    'antlr', 'debian',
                                    'README.gNewSense')
        with open(gns_readme_file, 'rb') as f:
            assert f.read() == b'Changed-From-Debian: Removed example with non-free files.\nChange-Type: Modified\n\nFor gNewSense, the non-free unicode.IDENTs files are *actually* removed (see\nalso README.source). See gNewSense bug #34218 for details.\n'


    def test_slurp_gns_readme_error(self):
        saved = slurp_gns_readme('parkes', 'non-existent-pkg', self.gns_pkgs_dir)
        assert saved == False

        gns_readme_file = path.join(self.gns_pkgs_dir, 'parkes',
                                    'non-existent-pkg', 'debian',
                                    'README.gNewSense')
        assert not path.exists(gns_readme_file)


    def test_slurp_all_gns_readmes(self):
        pkgs = read_packages(self.small_pkgs_file)

        # expected packages with no readmes
        expected_pkgs_noreadmes = [
            'pkg-with-no-readme',
            'another-pkgs-no-readme',
        ]

        pkgs_noreadmes = slurp_all_gns_readmes('parkes', pkgs, self.gns_pkgs_dir)
        assert_equal(pkgs_noreadmes, expected_pkgs_noreadmes)


    def test_read_gns_readme(self):
        # first download the antlr readme
        saved = slurp_gns_readme('parkes', 'antlr', self.gns_pkgs_dir)
        assert saved

        antlr_readme_content = read_gns_readme('parkes', 'antlr', self.gns_pkgs_dir)
        expected_antlr_readme_content = 'Changed-From-Debian: Removed example with non-free files.\nChange-Type: Modified\n\nFor gNewSense, the non-free unicode.IDENTs files are *actually* removed (see\nalso README.source). See gNewSense bug #34218 for details.\n'

        assert_equal(antlr_readme_content, expected_antlr_readme_content)


    def test_slurp_fields_from_readme(self):
        readme_content = ''
        field_values = slurp_fields_from_readme(readme_content)
        assert_equal(field_values['Change-Type'], None)
        assert_equal(field_values['Changed-From-Debian'], None)

        readme_content = 'Changed-From-Debian: \n'
        field_values = slurp_fields_from_readme(readme_content)
        assert_equal(field_values['Change-Type'], None)
        assert_equal(field_values['Changed-From-Debian'], None)

        readme_content = 'Change-Type: Deblob\n'
        field_values = slurp_fields_from_readme(readme_content)
        assert_equal(field_values['Change-Type'], 'Deblob')
        assert_equal(field_values['Changed-From-Debian'], None)

        readme_content = 'Changed-From-Debian: \nChange-Type: \n'
        field_values = slurp_fields_from_readme(readme_content)
        assert_equal(field_values['Change-Type'], None)
        assert_equal(field_values['Changed-From-Debian'], None)

        readme_content = 'Changed-From-Debian: Branding.    \nChange-Type: \n'
        field_values = slurp_fields_from_readme(readme_content)
        assert_equal(field_values['Change-Type'], None)
        assert_equal(field_values['Changed-From-Debian'], 'Branding.')

        readme_content = 'Changed-From-Debian: \nChange-Type: Modified'
        field_values = slurp_fields_from_readme(readme_content)
        assert_equal(field_values['Change-Type'], 'Modified')
        assert_equal(field_values['Changed-From-Debian'], None)

        readme_content = 'Changed-From-Debian:Fixed ambiguous use of the word free.\n\n\nChange-Type:Deblob\n'
        field_values = slurp_fields_from_readme(readme_content)
        assert_equal(field_values['Change-Type'], 'Deblob')
        assert_equal(field_values['Changed-From-Debian'],
                     'Fixed ambiguous use of the word free.')

        readme_content  = 'Changed-From-Debian: Removed example with non-free files.\nChange-Type: Modified\n\nFor gNewSense, the non-free unicode.IDENTs files are *actually* removed (see\nalso README.source). See gNewSense bug #34218 for details.\n'
        field_values = slurp_fields_from_readme(readme_content)
        assert_equal(field_values['Change-Type'], 'Modified')
        assert_equal(field_values['Changed-From-Debian'],
                     'Removed example with non-free files.')


    def test_config_dir(self):
        def env(e):
            return self.test_home

        with mock.patch('os.getenv', new=env):
            c_dir = config_dir()
            assert_equal(c_dir, os.path.join(self.test_home,
                                             '.config', 'gns-deb-diff'))


    def test_config_file(self):
        def env(e):
            return self.test_home

        with mock.patch('os.getenv', new=env):
            c_file = config_file()
            assert_equal(c_file, os.path.join(self.test_home, '.config',
                                             'gns-deb-diff', 'config'))


    def test_configured_p_no(self):
        def env(e):
            return self.test_home

        with mock.patch('os.getenv', new=env):
            configured = configured_p()
            assert_equal(configured, False)


    def test_configured_p_yes(self):
        def env(e):
            return self.test_home

        with mock.patch('os.getenv', new=env):
            c_path = config_dir()
            c_file = config_file()

            os.makedirs(c_path)
            open(c_file, 'w').close()

            configured = configured_p()
            assert_equal(configured, True)


    def teardown(self):
        """Teardown method for this class."""
        if(path.exists(self.gns_pkgs_dir)):
            os.chmod(self.gns_pkgs_dir, mode=0o700)
            rmtree(self.gns_pkgs_dir)

        if(path.exists(self.test_home)):
            rmtree(self.test_home)

        # restore sys.stderr
        sys.stderr = self.stderr_orig
