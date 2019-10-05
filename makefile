#!/usr/bin/env bash

YARPC=yarpc
TEST_DIR=tests

.PHONY: createVirtualenv
createVirtualenv:
	rm -rf env
	python3 -m pip install --user virtualenv
	python3 -m venv env
	source env/bin/activate

.PHONY: preInstall
preInstall:
	pip install --upgrade pip
	pip install -r $(TEST_DIR)/utils/requirements.txt
	pip install -U pytest
	pytest --version

.PHONY: test
test: .cleanCoverage
	pytest $(TEST_DIR)/unit

.cleanCoverage:
	@echo 'cleaning coverage files ...'
	rm -f .coverage
	rm -fr htmlcov/

.PHONY: openReport
openReport: .cleanCoverage
	coverage run --branch -m unittest discover --pattern '*_test.py' --start-directory $(TEST_DIR)
	coverage report --show-missing --include $(YARPC)/'*.py'
	coverage html --title 'Tests Coverage Report' --include $(YARPC)/'*.py'
	open htmlcov/index.html

.PHONY: help
help:
	@echo 'createVirtualenv - '
	@echo 'preInstall - '
	@echo 'test - run unit tests on all Python files'
	@echo 'openReport - check code coverage of all Python files'
