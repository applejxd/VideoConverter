# docs/Makefile
SPHINX_SRC_DIR    = ./docs/sphinx/source
SPHINX_BUILD_DIR     = ./docs/sphinx/build
SPHINX_OPTS   ?=

.PHONY: help html clean livehtml

help:
	@echo "Targets:"
	@echo "  html      Build HTML docs into $(SPHINX_BUILD_DIR)/html"
	@echo "  clean     Remove build dir"
	@echo "  livehtml  Auto-build + serve (needs sphinx-autobuild)"

html:
	sphinx-build -M html "$(SPHINX_SRC_DIR)" "$(SPHINX_BUILD_DIR)" $(SPHINX_OPTS)

clean:
	rm -rf "$(SPHINX_BUILD_DIR)"

livehtml:
	sphinx-autobuild "$(SPHINX_SRC_DIR)" "$(SPHINX_BUILD_DIR)/html" --open-browser
