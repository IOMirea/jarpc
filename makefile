SHELL:=/usr/bin/env bash

# variables
PYTHONPATH=$(shell echo " pwd :$$PYTHONPATH")
COVERAGE_DIR='coverage_data'
TEST_DIR=tests/unit

.PHONY: createVirtualenv
createVirtualenv:
	rm -rf env/
	python3 -m pip install --user virtualenv
	python3 -m venv env
	source env/bin/activate

########
# TEST #
########
.PHONY: test
test: .coverage
	@echo
	@echo '#################'
	@echo 'Testing Completed'

.coverage: cleanCoverage
	@PYTHONBREAKPOINT=0 \
	PYTHONPATH=$(PYTHONPATH)
	pip3 install coverage
	coverage run --branch -m unittest discover --verbose --pattern '*_test.py' --start-directory $(TEST_DIR) --top-level-directory '.'

.PHONY: cleanCoverage
cleanCoverage:
	@echo 'cleaning coverage files ...'
	@rm -rf $(COVERAGE_DIR)
	@rm -rf .coverage

.PHONY: help
help:
	@echo 'List all the make tergets available for use with "make list"'

.PHONY: list
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
