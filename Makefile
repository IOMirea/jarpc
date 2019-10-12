YARPC=yarpc
SOURCES=$(YARPC) examples
TEST_DIR=tests
PYTHON?=python3
PIP?=pip
PYTEST?=pytest

.PHONY: create-env
create-env:
	rm -rf env
	$(PYTHON) -m $(PIP) install --user virtualenv
	$(PYTHON) -m venv env
	source env/bin/activate

.PHONY: install
install:
	$(PIP) install --upgrade pip
# 	$(PYTHON) setup.py check -rms
	$(PIP) install -r $(TEST_DIR)/utils/requirements.txt
	$(PIP) install pre-commit pytest pytest-cov codecov

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
ci-test: lint
	$(PYTEST) --cov --cov-report=xml -v

.PHONY: flake8
flake8:
	flake8 $(SOURCES)

.PHONY: black
black:
	black $(SOURCES) --check

.PHONY: mypy
mypy:
	mypy $(SOURCES)

.PHONY: isort
isort:
	isort $(SOURCES) -rc --check-only

.PHONY: lint
lint: flake8 black mypy isort
	@echo 'Linting with flake8, black & mypy'

.PHONY: help
help:
	@echo 'HELP...................................................................'
	@echo 'create-env - creates a virtualenv'
	@echo 'install - installs all pre-requisites to run tests and coverage report'
	@echo 'test - runs unit tests on all Python files'
	@echo 'open-report - checks code coverage of all Python files'
	@echo 'lint - runs flake8, black, mypy, & isort Python files '
	@echo ''
