#  This file is part of gns-deb-diff.
#
#  gns-deb-diff is under the Public Domain. See
#  <https://creativecommons.org/publicdomain/zero/1.0>

test:
	@nosetests
.PHONY: test

build-dist:
	@python setup.py sdist bdist_wheel
.PHONY: build-dist

egg:
	@python setup.py egg_info
.PHONY: egg

upload:
	@twine upload -r pypi -s -i \
		'1534 126D 8C8E AD29 EDD9  1396 6BE9 3D8B F866 4377' \
		dist/*.tar.gz
	@twine upload -r pypi -s -i \
		'1534 126D 8C8E AD29 EDD9  1396 6BE9 3D8B F866 4377' \
		dist/*.whl
.PHONY: upload

clean-build:
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info

clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +

clean-venv:
	@rm -rf bin/
	@rm -rf include/
	@rm -rf lib/
	@rm -rf local/
	@rm -rf man/
.PHONY: clean-venv
