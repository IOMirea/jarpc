YARPC=yarpc
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
	$(PIP) install .
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
	@find . -type d -name 'env' -prune -o -name 'docs' -prune -o -name '*.py' -exec flake8 "{}" +
	@echo 'flake8....................................................................Passed'

.PHONY: black
black:
	@find . -type d -name 'env' -prune -o -name 'docs' -prune -o -name '*.py' -exec black "{}" +
	@echo 'black.....................................................................Passed'

.PHONY: mypy
mypy:
	@find . -type d -name 'env' -prune -o -name 'docs' -prune -o -name '*.py' -exec mypy --ignore-missing-imports "{}" +
	@echo 'mypy......................................................................Passed'

.PHONY: lint
lint: flake8 black mypy
	@echo 'Linting with flake8, black & mypy'

.PHONY: help
help:
	@echo '==================================== HELP  ===================================='
	@echo 'create-env - creates a virtualenv'
	@echo 'install - install all run pre requisites to run tests and coverage report'
	@echo 'test - run unit tests on all Python files'
	@echo 'open-report - check code coverage of all Python files'
	@echo 'lint - run pylint and flake8 on all your Python files'
	@echo ''
