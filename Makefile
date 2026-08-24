# Makefile
SPHINX_SRC_DIR   = ./docs/sphinx/source
SPHINX_BUILD_DIR = ./docs/sphinx/build
SPHINX_OPTS     ?=

.PHONY: help html clean livehtml test lint format check

help:
	@echo "Targets:"
	@echo "  html      Build HTML docs into $(SPHINX_BUILD_DIR)/html"
	@echo "  livehtml  Auto-build + serve the docs in a browser"
	@echo "  clean     Remove the docs build dir and generated API sources"
	@echo "  test      Run the test suite with pytest"
	@echo "  lint      Run ruff check and verify formatting"
	@echo "  format    Apply ruff autofixes and formatting"
	@echo "  check     Run lint, test and html"

html:
	uv run sphinx-build -M html "$(SPHINX_SRC_DIR)" "$(SPHINX_BUILD_DIR)" $(SPHINX_OPTS)

clean:
	rm -rf "$(SPHINX_BUILD_DIR)" "$(SPHINX_SRC_DIR)/api"

livehtml:
	uv run sphinx-autobuild "$(SPHINX_SRC_DIR)" "$(SPHINX_BUILD_DIR)/html" --open-browser

test:
	uv run pytest

lint:
	uv run ruff check src tests
	uv run ruff format --check src tests

format:
	uv run ruff check --fix src tests
	uv run ruff format src tests

check: lint test html
