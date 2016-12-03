#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of gns-deb-diff.
#
#  gns-deb-diff is under the Public Domain. See
#  <https://creativecommons.org/publicdomain/zero/1.0>

import builtins
import json
import os
import subprocess
import sys

import gd_diff

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
        self.tiny_pkgs_file = 'tests/files/tiny-parkes-pkgs.list'
        self.pkgs_file_ne = 'tests/nonexistent-file.list'
        self.gns_pkgs_dir = 'tests/gns-pkgs'
        self.test_home = 'tests/HOME'
        self.test_w_file = os.path.join(self.test_home, 'w_file')

        self.stderr_orig = sys.stderr

        # make test home
        os.mkdir(self.test_home, mode=0o700)

        self.env_func = lambda e: self.test_home


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
        pkgs = read_packages(self.pkgs_file)
        assert len(pkgs) == 82


    def test_read_packages_sanity(self):
        pkgs = read_packages(self.pkgs_file)

        for pkg in pkgs:
            assert not ' ' in pkg


    @raises(SystemExit)
    def test_get_packages_error(self):
        res = get_packages('foo_release')


    def test_get_packages(self):
        pkgs = get_packages('parkes')

        assert_equal(pkgs, 'antlr\napt\napt-setup\nautoconf\nautoconf2.59\nautoconf2.64\nbacula\nbase-files\nbase-installer\nbatik\ncairomm\ncdebootstrap\ncfitsio3\nchoose-mirror\nclaws-mail\ndb4.6\ndb4.7\ndb4.8\ndebian-cd\ndebian-edu\ndebian-installer\ndebian-installer-launcher\ndebootstrap\ndesktop-base\ndoc-linux\ndoc-linux-hr\ndoc-linux-it\ndoc-linux-ja\ndoc-linux-pl\nenscript\nepiphany-browser\nfop\nfreetype\ngalaxia\ngdm3\nglibmm2.4\ngnewsense-archive-keyring\ngnome-desktop\ngtkmm2.4\nicedove\niceweasel\nkde4libs\nkdebase\nkdebase-workspace\nkdenetwork\nkernel-wedge\nlensfun\nliferea\nlintian\nlinux-2.6\nlinux-kernel-di-amd64-2.6\nlinux-kernel-di-i386-2.6\nlinux-latest-2.6\nlive-build\nlive-config\nmeta-gnome2\nmplayer\nnet-retriever\nobjcryst-fox\nopenbox-themes\nopenjdk-6\nopenoffice.org\npangomm\nperl-tk\npkgsel\npopularity-contest\npsutils\npython-apt\nscreenlets\nsip4-qt3\nsoftware-center\ntcl8.4\ntcl8.5\ntexlive-extra\ntk8.4\ntk8.5\nupdate-manager\nvim\nwmaker\nxchat\nxdm\nxorg-server\nxserver-xorg-video-siliconmotion\nyeeloong-base\n')


    def test_config_dir(self):
        with mock.patch('os.getenv', new=self.env_func):
            c_dir = config_dir()
            assert_equal(c_dir, os.path.join(self.test_home,
                                             '.config', 'gns-deb-diff'))
            assert_equal(os.path.isdir(c_dir), True)


    def test_config_file(self):
        with mock.patch('os.getenv', new=self.env_func):
            c_file = config_file()
            assert_equal(c_file, os.path.join(self.test_home, '.config',
                                             'gns-deb-diff', 'config'))


    def test_read_config_file_fail(self):
        config = read_config_file()
        assert_equal(config, False)


    def test_read_config_file_success(self):
        with mock.patch('os.getenv', new=self.env_func):
            c_file = config_file()

            # first write sample config file.
            json.dump({'user': 'usrnm', 'pass': 'weasaspeciesrfckd'},
                      open(c_file, 'w'))

            # now on to the test.
            config = read_config_file()
            assert_equal(config['user'], 'usrnm')
            assert_equal(config['pass'], 'weasaspeciesrfckd')


    def test_pkgs_dir(self):
        with mock.patch('os.getenv', new=self.env_func):
            pd = pkgs_dir()
            assert_equal(pd, os.path.join(self.test_home, '.config',
                                          'gns-deb-diff', 'pkgs'))
            assert_equal(os.path.isdir(pd), True)


    def test_mk_pkgs_list(self):
        with mock.patch('os.getenv', new=self.env_func):
            pkgs_file = mk_pkgs_list('parkes')
            # test
            assert_equal(read_file(pkgs_file), 'antlr\napt\napt-setup\nautoconf\nautoconf2.59\nautoconf2.64\nbacula\nbase-files\nbase-installer\nbatik\ncairomm\ncdebootstrap\ncfitsio3\nchoose-mirror\nclaws-mail\ndb4.6\ndb4.7\ndb4.8\ndebian-cd\ndebian-edu\ndebian-installer\ndebian-installer-launcher\ndebootstrap\ndesktop-base\ndoc-linux\ndoc-linux-hr\ndoc-linux-it\ndoc-linux-ja\ndoc-linux-pl\nenscript\nepiphany-browser\nfop\nfreetype\ngalaxia\ngdm3\nglibmm2.4\ngnewsense-archive-keyring\ngnome-desktop\ngtkmm2.4\nicedove\niceweasel\nkde4libs\nkdebase\nkdebase-workspace\nkdenetwork\nkernel-wedge\nlensfun\nliferea\nlintian\nlinux-2.6\nlinux-kernel-di-amd64-2.6\nlinux-kernel-di-i386-2.6\nlinux-latest-2.6\nlive-build\nlive-config\nmeta-gnome2\nmplayer\nnet-retriever\nobjcryst-fox\nopenbox-themes\nopenjdk-6\nopenoffice.org\npangomm\nperl-tk\npkgsel\npopularity-contest\npsutils\npython-apt\nscreenlets\nsip4-qt3\nsoftware-center\ntcl8.4\ntcl8.5\ntexlive-extra\ntk8.4\ntk8.5\nupdate-manager\nvim\nwmaker\nxchat\nxdm\nxorg-server\nxserver-xorg-video-siliconmotion\nyeeloong-base\n')


    def test_readmes_dir(self):
        with mock.patch('os.getenv', new=self.env_func):
            rd_parkes = readmes_dir('parkes')
            assert_equal(rd_parkes, os.path.join(self.test_home, '.config',
                                                 'gns-deb-diff', 'readmes',
                                                 'parkes'))
            assert_equal(os.path.isdir(rd_parkes), True)


    def test_wiki_page_dir(self):
        with mock.patch('os.getenv', new=self.env_func):
            wd_parkes = wiki_page_dir('parkes')
            assert_equal(wd_parkes, os.path.join(self.test_home, '.config',
                                                 'gns-deb-diff', 'wiki-page',
                                                 'parkes'))
            assert_equal(os.path.isdir(wd_parkes), True)


    def test_write_wiki_page(self):
        with mock.patch('os.getenv', new=self.env_func):
            release = 'parkes'
            write_wiki_page(release, 'wiki content')
            wp_file = os.path.join(wiki_page_dir(release), 'last.rev')
            assert_equal(read_file(wp_file), 'wiki content')


    def test_configured_p_no(self):
        with mock.patch('os.getenv', new=self.env_func):
            configured = configured_p()
            assert_equal(configured, False)


    def test_configured_p_yes(self):
        with mock.patch('os.getenv', new=self.env_func):
            c_path = config_dir()
            c_file = config_file()

            open(c_file, 'w').close()

            configured = configured_p()
            assert_equal(configured, True)


    def test_configure(self):
        inputs = ['usrnm', 'weasaspeciesrfckd']
        def mock_input(p):
            return inputs.pop(0)

        with mock.patch('os.getenv', new=self.env_func), \
             mock.patch('builtins.input', new=mock_input):
            configure()

            # read config file
            config = json.load(open(config_file(), 'r'))

            # tests
            assert_equal(config['user'], 'usrnm')
            assert_equal(config['pass'], 'weasaspeciesrfckd')
            assert_equal(oct(os.stat(config_file()).st_mode), '0o100600')


    def test_save_gns_readme(self):
        with mock.patch('os.getenv', new=self.env_func):
            cmd = 'bzr cat bzr://bzr.sv.gnu.org/gnewsense/packages-parkes/antlr/debian/README.gNewSense'
            cp = execute(cmd, out=subprocess.PIPE)
            readme_content = cp.stdout.decode() # convert to str

            # save it
            save_gns_readme(readme_content, 'parkes', 'antlr')

            gns_readme_file = path.join(self.test_home, '.config',
                                        'gns-deb-diff', 'readmes',
                                        'parkes', 'antlr', 'debian',
                                        'README.gNewSense')
            with open(gns_readme_file, 'rb') as f:
                assert f.read() == b'Changed-From-Debian: Removed example with non-free files.\nChange-Type: Modified\n\nFor gNewSense, the non-free unicode.IDENTs files are *actually* removed (see\nalso README.source). See gNewSense bug #34218 for details.\n'


    def test_save_gns_readme_double(self):
        with mock.patch('os.getenv', new=self.env_func):
            cmd = 'bzr cat bzr://bzr.sv.gnu.org/gnewsense/packages-parkes/antlr/debian/README.gNewSense'
            cp = execute(cmd, out=subprocess.PIPE)
            readme_content = cp.stdout.decode() # convert to str

            # save it twice
            save_gns_readme(readme_content, 'parkes', 'antlr')
            save_gns_readme(readme_content, 'parkes', 'antlr')

            gns_readme_file = path.join(self.test_home, '.config',
                                        'gns-deb-diff', 'readmes',
                                        'parkes', 'antlr', 'debian',
                                        'README.gNewSense')
            with open(gns_readme_file, 'rb') as f:
                assert f.read() == b'Changed-From-Debian: Removed example with non-free files.\nChange-Type: Modified\n\nFor gNewSense, the non-free unicode.IDENTs files are *actually* removed (see\nalso README.source). See gNewSense bug #34218 for details.\n'


    def test_slurp_gns_readme_success(self):
        with mock.patch('os.getenv', new=self.env_func):
            saved = slurp_gns_readme('parkes', 'antlr')
            assert saved == True

            gns_readme_file = path.join(self.test_home, '.config',
                                        'gns-deb-diff', 'readmes',
                                        'parkes', 'antlr', 'debian',
                                        'README.gNewSense')
            with open(gns_readme_file, 'rb') as f:
                assert f.read() == b'Changed-From-Debian: Removed example with non-free files.\nChange-Type: Modified\n\nFor gNewSense, the non-free unicode.IDENTs files are *actually* removed (see\nalso README.source). See gNewSense bug #34218 for details.\n'


    def test_slurp_gns_readme_error(self):
        with mock.patch('os.getenv', new=self.env_func):
            saved = slurp_gns_readme('parkes', 'non-existent-pkg')
            assert saved == False

            gns_readme_file = path.join(self.test_home, '.config',
                                        'gns-deb-diff', 'readmes',
                                        'parkes', 'non-existent-pkg',
                                        'debian', 'README.gNewSense')
            assert not path.exists(gns_readme_file)


    def test_slurp_all_gns_readmes(self):
        with mock.patch('os.getenv', new=self.env_func):
            pkgs = read_packages(self.small_pkgs_file)

            # expected packages with no readmes
            expected_pkgs_noreadmes = [
                'pkg-with-no-readme',
                'another-pkg-no-readme',
            ]

            pkgs_noreadmes = slurp_all_gns_readmes('parkes', pkgs)
            assert_equal(pkgs_noreadmes, expected_pkgs_noreadmes)


    def test_read_gns_readme(self):
        # first download the antlr readme
        saved = slurp_gns_readme('parkes', 'antlr')
        assert saved

        antlr_readme_content = read_gns_readme('parkes', 'antlr')
        expected_antlr_readme_content = 'Changed-From-Debian: Removed example with non-free files.\nChange-Type: Modified\n\nFor gNewSense, the non-free unicode.IDENTs files are *actually* removed (see\nalso README.source). See gNewSense bug #34218 for details.\n'
        assert_equal(antlr_readme_content, expected_antlr_readme_content)


    def test_read_gns_readme_none(self):
        readme_content = read_gns_readme('parkes', 'non-existent-pkg')
        assert_equal(readme_content, None)


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


    def test_get_wiki_page_data(self):
        def mock_mk_pkgs_list(r):
            return self.small_pkgs_file

        pkgs = [p.strip()
                for p in open(self.small_pkgs_file, 'r').read() \
                .split('\n')]

        with mock.patch('os.getenv', new=self.env_func), \
             mock.patch('gd_diff.mk_pkgs_list', new=mock_mk_pkgs_list):
            pkgs_noreadmes, table_data = get_wiki_page_data('parkes')

            for pkg in pkgs_noreadmes:
                assert pkg in ['pkg-with-no-readme', 'another-pkg-no-readme']

            for pkg, field_values in table_data.items():
                assert pkg in pkgs
                for field, value in field_values.items():
                    assert field in gd_diff.field_list
                    assert (type(value) == str or
                            value is None)

    def test_construct_table_row(self):
        row = construct_table_row('antlr', 'Modified',
                                  'Removed example with non-free files')
        columns = row.split('||')[1:]
        assert_equal(columns[0], 'antlr')
        assert_equal(columns[1], 'Modified')
        assert_equal(columns[2], 'Removed example with non-free files')
        assert_equal(columns[3] , '[[http://bzr.savannah.gnu.org/lh/gnewsense/packages-parkes/antlr/annotate/head:/debian/README.gNewSense|more_info]]')

        row = construct_table_row('antlr', None,
                                  'Removed example with non-free files')
        columns = row.split('||')[1:]
        assert_equal(columns[0], 'antlr')
        assert_equal(columns[1], ' ')
        assert_equal(columns[2], 'Removed example with non-free files')
        assert_equal(columns[3] , '[[http://bzr.savannah.gnu.org/lh/gnewsense/packages-parkes/antlr/annotate/head:/debian/README.gNewSense|more_info]]')

        row = construct_table_row('antlr', 'Modified',
                                  None)
        columns = row.split('||')[1:]
        assert_equal(columns[0], 'antlr')
        assert_equal(columns[1], 'Modified')
        assert_equal(columns[2], ' ')
        assert_equal(columns[3] , '[[http://bzr.savannah.gnu.org/lh/gnewsense/packages-parkes/antlr/annotate/head:/debian/README.gNewSense|more_info]]')

        row = construct_table_row('antlr', None,
                                  None)
        columns = row.split('||')[1:]
        assert_equal(columns[0], 'antlr')
        assert_equal(columns[1], ' ')
        assert_equal(columns[2], ' ')
        assert_equal(columns[3] , '[[http://bzr.savannah.gnu.org/lh/gnewsense/packages-parkes/antlr/annotate/head:/debian/README.gNewSense|more_info]]')


    def test_generate_wiki_table(self):
        def mock_mk_pkgs_list(r):
            return self.tiny_pkgs_file

        pkgs = [p.strip()
                for p in open(self.tiny_pkgs_file, 'r').read() \
                .split('\n')]

        expected_pkgs_noreadmes = ['pkg-with-no-readme',
                                   'another-pkg-no-readme']

        with mock.patch('os.getenv', new=self.env_func), \
             mock.patch('gd_diff.mk_pkgs_list', new=mock_mk_pkgs_list):
            pkgs_noreadmes, wiki_page = generate_wiki_table('parkes')

            for pkg in pkgs_noreadmes:
                assert pkg in expected_pkgs_noreadmes

            pkgs = set(pkgs) - set(expected_pkgs_noreadmes)

            for row in wiki_page.split('\n')[:-1]:
                cols = row.split('||')[1:]
                pkg = cols[0]

                assert pkg in pkgs
                assert cols[3] == '[[{}|more_info]]'.format(
                    bzr_pkg_readme_fmt.format(pkg))

                pkgs.remove(pkg)

            assert len(pkgs) == 0


    def teardown(self):
        """Teardown method for this class."""
        if(path.exists(self.gns_pkgs_dir)):
            os.chmod(self.gns_pkgs_dir, mode=0o700)
            rmtree(self.gns_pkgs_dir)

        if(path.exists(self.test_home)):
            rmtree(self.test_home)

        # restore sys.stderr
        sys.stderr = self.stderr_orig
