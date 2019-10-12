YARPC=yarpc
TEST_DIR=tests
PYTHON?=python3
PIP3?=pip3
PYTEST?=pytest

.PHONY: create-env
create-env:
	rm -rf env
	$(PYTHON) -m $(PIP3) install --user virtualenv
	$(PYTHON) -m venv env
	source env/bin/activate

.PHONY: install
install:
	$(PIP3) install --upgrade pip
	$(PIP3) install .
	$(PIP3) install -r $(TEST_DIR)/utils/requirements.txt
	$(PIP3) install pre-commit pytest pytest-cov codecov

.PHONY: test
test: .cleanCoverage
	$(PYTEST) $(TEST_DIR)/unit -v

.cleanCoverage:
	@echo 'cleaning coverage files ...'
	rm -rf .coverage htmlcov/

.PHONY: open-report
open-report: .cleanCoverage
	$(PYTEST) --cov=$(YARPC) --cov-report=term-missing --cov-report=html
	open htmlcov/index.html

.PHONY: ci-test
ci-test:
	pre-commit run --all-files
	$(PYTEST) --cov --cov-report=xml -v

.PHONY: lint
lint:
	flake8 $(YARPC)/"*.py"
	mypy $(YARPC)
	black $(YARPC)

.PHONY: help
help:
	@echo '==================================== HELP  ===================================='
	@echo 'create-env - creates a virtualenv'
	@echo 'install - install all run pre requisites to run tests and coverage report'
	@echo 'test - run unit tests on all Python files'
	@echo 'open-report - check code coverage of all Python files'
	@echo 'lint - run pylint and flake8 on all your Python files'
	@echo ''
