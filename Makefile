# = Makefile
#
# Automate some regular actions
#
#
.PHONY: test build upload clean

.ONESHELL:
SHELL := /bin/bash

all:
	@echo "    init-env"
	@echo "        Use like 'eval $$(make init-env)'"
	@echo "    lint"
	@echo "        Check style with flake8."
	@echo "    test"
	@echo "        Run pytest"
	@echo "    build"
	@echo "        Build packages"
	@echo "    upload"
	@echo "        Upload the packages to Pypi"
	@echo "    clean-pyc"
	@echo "        Remove python artifacts."
	@echo "    clean-build"
	@echo "        Remove build artifacts."


# Helpers
init-env:
	@echo "export PATH=$$(pwd)/tools/bin:${PATH}"


# Tests
lint:
	export PATH=$$(pwd)/tools/bin:${PATH} \
	&& cd src/ \
	&& flake8

test: clean-pyc
	cd src/ \
	&& python setup.py test


# Actions
build:
	cp README.md src/ \
	&& cd src/ \
	&& python setup.py sdist \
	&& rm README.md

upload:
	export PATH=$$(pwd)/tools/bin:${PATH} \
	&& twine upload --repository testpypi src/dist/*


# Clean
clean-build:
	cd src/
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

clean-tests:
	git checkout -- tests/docker-compose/puppetserver
	rm -rf tests/docker-compose/puppetca_cli/

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +


clean: clean-pyc clean-build clean-tests
