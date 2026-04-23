# Regenerate tutorial test scripts from the Markdown source files.
#
# Each tutorial page is written in Markdown. Shell commands inside ```shell
# fenced code blocks are extracted by extract_commands.py and written into
# numbered .sh scripts that the spread test suite can execute directly.
#
# Run from the project root:
#   make -f python/tests/tutorial/Makefile
#
# Or from this directory:
#   make

# ---------------------------------------------------------------------------
# Python interpreter
# ---------------------------------------------------------------------------
PYTHON   ?= python3

# ---------------------------------------------------------------------------
# Path variables
# ---------------------------------------------------------------------------
THIS_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
ROOT     := $(abspath $(THIS_DIR)/../../..)
EXTRACT  := $(THIS_DIR)extract_commands.py

# ---------------------------------------------------------------------------
# Script → Markdown mapping (SCRIPTS)
# ---------------------------------------------------------------------------
SCRIPTS := \
    $(THIS_DIR)1-environment-setup.sh:$(ROOT)/docs/tutorial/1-environment-setup.md \
    $(THIS_DIR)2-distributed-data-processing.sh:$(ROOT)/docs/tutorial/2-distributed-data-processing.md \
    $(THIS_DIR)3-data-stream-processing.sh:$(ROOT)/docs/tutorial/3-data-stream-processing.md \
    $(THIS_DIR)4-history-server.sh:$(ROOT)/docs/tutorial/4-history-server.md \
    $(THIS_DIR)5-monitoring-with-cos.sh:$(ROOT)/docs/tutorial/5-monitoring-with-cos.md \
    $(THIS_DIR)6-apache-kyuubi.sh:$(ROOT)/docs/tutorial/6-apache-kyuubi.md \
    $(THIS_DIR)7-wrapping-up.sh:$(ROOT)/docs/tutorial/7-wrapping-up.md

OUTPUTS := $(foreach pair,$(SCRIPTS),$(word 1,$(subst :, ,$(pair))))

# ---------------------------------------------------------------------------
# rel — convert an absolute path back to a root-relative path
# ---------------------------------------------------------------------------
rel = $(patsubst $(ROOT)/%,%,$(1))

# ---------------------------------------------------------------------------
# Target: all (default)
# ---------------------------------------------------------------------------
.PHONY: all
all: $(OUTPUTS)

# ---------------------------------------------------------------------------
# Per-script build rules (generated with define … endef)
# ---------------------------------------------------------------------------
define make_rule
$(word 1,$(subst :, ,$(1))): $(word 2,$(subst :, ,$(1))) $(EXTRACT)
	cd $(ROOT) && $(PYTHON) $(call rel,$(EXTRACT)) $(call rel,$(word 2,$(subst :, ,$(1)))) $(call rel,$(word 1,$(subst :, ,$(1))))
endef
$(foreach pair,$(SCRIPTS),$(eval $(call make_rule,$(pair))))

# ---------------------------------------------------------------------------
# Target: extract
# ---------------------------------------------------------------------------
.PHONY: extract
extract:
	cd $(ROOT) && $(PYTHON) $(call rel,$(EXTRACT)) docs/tutorial/ python/tests/tutorial/

# ---------------------------------------------------------------------------
# Target: help
# ---------------------------------------------------------------------------
.PHONY: help
help:
	@echo "Usage: make -f python/tests/tutorial/Makefile [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all       Regenerate scripts that are out of date (default)"
	@echo "  extract   Unconditionally regenerate all scripts"
	@echo "  test      Run the full tutorial suite (abort on first failure)"
	@echo "  test-continue  Run all stages even if earlier ones fail"
	@echo "  test-debug     Run with -debug: drop into a shell on failure"
	@echo "  help      Show this help message"
	@echo ""

# ---------------------------------------------------------------------------
# Spread configuration
# ---------------------------------------------------------------------------
SPREAD     ?= spread
SPREAD_JOB ?= multipass:ubuntu-24.04-64:python/tests/tutorial/

# ---------------------------------------------------------------------------
# Target: test (default run — abort on first failure)
# ---------------------------------------------------------------------------
.PHONY: test
test: extract
	$(SPREAD) -abend -vv $(SPREAD_JOB)

# ---------------------------------------------------------------------------
# Target: test-continue (run all stages even if some fail)
# ---------------------------------------------------------------------------
.PHONY: test-continue
test-continue: extract
	$(SPREAD) -vv $(SPREAD_JOB)

# ---------------------------------------------------------------------------
# Target: test-debug (abort on first failure, drop into VM shell)
# ---------------------------------------------------------------------------
.PHONY: test-debug
test-debug: extract
	$(SPREAD) -abend -vv -debug $(SPREAD_JOB)
