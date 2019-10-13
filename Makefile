PYTHON ?= python3
PIP ?= pip

# TODO: check examples with some linters (no mypy?)
SOURCES = yarpc examples setup.py

# TODO: this is hardcoded examples list, but it should be dynamic.
# the reason for this is that some examples run forever currently.
EXAMPLES = examples/response_iterator.py

.PHONY: create-env
create-env:
	rm -rf env
	$(PYTHON) -m pip install --user virtualenv
	$(PYTHON) -m venv env
	source env/bin/activate

.PHONY: install
install:
	$(PIP) install --upgrade pip
	$(PIP) install .
	$(PIP) install -r requirements/dev.txt

.PHONY: test
test:
	pytest tests/unit -v

.PHONY: open-report
open-report: .clean-cov
	pytest --cov=yarpc --cov-report=term-missing --cov-report=html
	open file://`pwd`/htmlcov/index.html

.clean-cov:
	@echo 'cleaning coverage files ...'
	rm -rf .coverage coverage.xml htmlcov/

.PHONY: clean
clean: .clean-cov
	rm -rf docs/_build
	rm -rf build dist yarpc.egg-info
	rm -rf .mypy_cache
	rm -rf .pytest_cache

.PHONY: examples
examples: $(EXAMPLES)

.PHONY: $(EXAMPLES)
$(EXAMPLES):
	$(PYTHON) $@

.PHONY: ci-test
ci-test:
	pytest --cov --cov-report=xml -v

.PHONY: flake8
flake8:
	flake8 $(SOURCES)

.PHONY: black
black:
	black $(SOURCES)

.PHONY: black-check
black-check:
	black $(SOURCES) --check

.PHONY: mypy
mypy:
	mypy $(SOURCES)

.PHONY: isort
isort:
	isort $(SOURCES) -rc

.PHONY: isort-check
isort-check:
	isort $(SOURCES) -rc --check-only

.PHONY: lint
lint: flake8 black-check mypy isort-check
	$(PYTHON) setup.py check -rms

.PHONY: help
help:
	@echo 'Existing make targets:'
	@echo '  black         runs black'
	@echo '  black-check   runs black (no formatting)'
	@echo '  ci-test       intended for Travis. runs tests and coverage'
	@echo '  clean         cleans working directory'
	@echo '  create-env    creates a virtualenv'
	@echo '  examples      runs examples'
	@echo '  install       installs all pre-requisites to run tests and coverage'
	@echo '  isort         runs isort'
	@echo '  isort         runs isort (no formatting)'
	@echo '  lint          runs flake8, black, mypy, & isort (no formatting)'
	@echo '  test          checks coverage and opens html report'
	@echo '  open-report   checks code coverage of all Python files'
