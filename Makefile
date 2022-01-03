PYTHON ?= python3
PIP ?= pip

# TODO: check examples with some linters (no mypy?)
SOURCES = jarpc examples setup.py

# TODO: this is hardcoded examples list, but it should be dynamic.
# the reason for this is that some examples run forever currently.
EXAMPLES = examples/response_iterator.py examples/custom_encoder.py

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
test: .pytest-version
	pytest tests/unit -v

.PHONY: open-report
open-report: .clean-cov .pytest-version
	pytest --cov=jarpc --cov-report=term-missing --cov-report=html
	open file://`pwd`/htmlcov/index.html

.clean-cov:
	@echo 'cleaning coverage files ...'
	rm -rf .coverage coverage.xml htmlcov/

.PHONY: clean
clean: .clean-cov
	rm -rf docs/_build
	rm -rf build dist jarpc.egg-info
	rm -rf .mypy_cache
	rm -rf .pytest_cache

.PHONY: examples
examples: $(EXAMPLES)

.PHONY: $(EXAMPLES)
$(EXAMPLES):
	$(PYTHON) $@

.PHONY: ci-test
ci-test: .pytest-version
	pytest --cov --cov-report=xml -v

.PHONY: dist
dist: .twine-version
	$(PYTHON) setup.py check -ms
	$(PYTHON) setup.py sdist bdist_wheel
	twine check dist/*

.PHONY: flake8
flake8: .flake8-version
	flake8 $(SOURCES)

.PHONY: black
black: .black-version
	black $(SOURCES)

.PHONY: black-check
black-check: .black-version
	black $(SOURCES) --check

.PHONY: mypy
mypy: .mypy-version
	mypy $(SOURCES)

.PHONY: isort
isort: .isort-version
	isort $(SOURCES) -rc

.PHONY: .isort-check
isort-check: .isort-version
	isort $(SOURCES) -rc --check-only

.PHONY: lint
lint: flake8 black-check mypy isort-check
	$(PYTHON) setup.py check -ms

.%-version:
	@echo
	$* --version
	@echo

.PHONY: help
help:
	@echo 'Existing make targets:'
	@echo '  black         runs black'
	@echo '  black-check   runs black (no formatting)'
	@echo '  ci-test       intended for Travis. runs tests and coverage'
	@echo '  clean         cleans working directory'
	@echo '  create-env    creates a virtualenv'
	@echo '  dist          builds dist wheels and runs twine check'
	@echo '  examples      runs examples'
	@echo '  install       installs all pre-requisites to run tests and coverage'
	@echo '  isort         runs isort'
	@echo '  isort-check   runs isort (no formatting)'
	@echo '  lint          runs flake8, black, mypy, & isort (no formatting)'
	@echo '  test          checks coverage and opens html report'
	@echo '  open-report   checks code coverage of all Python files'
