YARPC=yarpc
TEST_DIR=tests/unit

.PHONY: create-env
create-env:
	rm -rf env
	python3 -m pip install --user virtualenv
	python3 -m venv env
	source env/bin/activate

.PHONY: install
install:
	pip install --upgrade pip
	pip install -r $(TEST_DIR)/utils/requirements.txt

.PHONY: test
test: .cleanCoverage
	pytest $(TEST_DIR)

.cleanCoverage:
	@echo 'cleaning coverage files ...'
	rm -f .coverage
	rm -fr htmlcov/

.PHONY: open-report
open-report: .cleanCoverage
	pytest --cov=$(YARPC) --cov-report=term-missing --cov-report=html
	open -a "Google Chrome" htmlcov/index.html

.PHONY: help
help:
	@echo '==================================== HELP  ===================================='
	@echo 'create-env - creates a virtualenv'
	@echo 'install - install all run pre requisites to run tests and coverage report'
	@echo 'test - run unit tests on all Python files'
	@echo 'open-report - check code coverage of all Python files'
	@echo 'lint - run pylint and flake8 on all your Python files'
	@echo ''
