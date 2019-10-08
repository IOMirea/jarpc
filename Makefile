YARPC=yarpc
TEST_DIR=tests
PYTHON?=python3
PIP?=pip
PYTEST?=pytest

.PHONY: create-env
create-env:
	rm -rf env
	$(PYTOHN) -m $(PIP) install --user virtualenv
	$(PYTOHN) -m venv env
	source env/bin/activate

.PHONY: install
install:
	$(PIP) install --upgrade $(PIP)
	$(PIP) install -r $(TEST_DIR)/utils/requirements.txt

.PHONY: test
test: .cleanCoverage
	$(PYTEST) $(TEST_DIR)/unit

.cleanCoverage:
	@echo 'cleaning coverage files ...'
	rm -f .coverage
	rm -fr htmlcov/

.PHONY: open-report
open-report: .cleanCoverage
	$(PYTEST) --cov=$(YARPC) --cov-report=term-missing --cov-report=html
	open htmlcov/index.html

.PHONY: help
help:
	@echo '==================================== HELP  ===================================='
	@echo 'create-env - creates a virtualenv'
	@echo 'install - install all run pre requisites to run tests and coverage report'
	@echo 'test - run unit tests on all Python files'
	@echo 'open-report - check code coverage of all Python files'
	@echo 'lint - run pylint and flake8 on all your Python files'
	@echo ''
