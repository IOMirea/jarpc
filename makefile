#!/usr/bin/env bash

# variables
COVERAGE_DIR='coverage_data'
TEST_DIR=tests/unit

.PHONY: createVirtualenv
createVirtualenv:
	python3 -m pip install --user virtualenv
	python3 -m venv env
	source env/bin/activate

########
# TEST #
########
.PHONY: preInstall
preInstall:
	pip install -U pytest
	pytest --version

.PHONY: test
test:
	pytest $(TEST_DIR)
	@echo 'Tests Completed'

.PHONY: help
help:
	@echo 'List all the make tergets available for use with "make list"'

.PHONY: list
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
