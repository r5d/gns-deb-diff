#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of gns-deb-diff.
#
#  gns-deb-diff is under the Public Domain. See
#  <https://creativecommons.org/publicdomain/zero/1.0>

import os
import sys

from nose.tools import *

from gd_diff import *

class TestGdDiff(object):

    def setup(self):
        """Setup method for this class."""
        self.pkgs_file = "tests/files/pkgs.list"
        self.pkgs_file_ne = 'tests/nonexistent-file.list'

    def test_read_file_success(self):
        f_content = read_file(self.pkgs_file)

        assert isinstance(f_content, str)
        assert_equal(len(f_content.split('\n')), 82)

    @raises(SystemExit)
    def test_read_file_error(self):
        with open(os.devnull, 'w') as sys.stderr:
            f_content = read_file(self.pkgs_file_ne)


    def test_get_packages(self):
        pkgs_iter = get_packages(self.pkgs_file)
        assert len(list(pkgs_iter)) == 82

    def test_get_packages_sanity(self):
        pkgs_iter = get_packages(self.pkgs_file)

        for pkg in pkgs_iter:
            assert not ' ' in pkg

    def teardown(self):
        """Teardown method for this class."""
        pass

