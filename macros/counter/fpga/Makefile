# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

# Dispatcher: forwards every target to the chosen board's own Makefile.
# The boards themselves are the folders holding a Makefile, so adding one
# is enough to make it selectable here. See ./README.md.

# Target board (default: pico-ice)
# Override with: make <target> BOARD=<board>
BOARD ?= pico-ice

# Extra options for the sak-open.py file browser (e.g. --all to include build outputs)
# Override with: make open OPEN_ARGS=<options>
OPEN_ARGS ?=

BOARDS := $(sort $(patsubst %/,%,$(dir $(wildcard */Makefile))))

.DEFAULT_GOAL := help


# Help Target
help: ## Show this help message
	@echo 'Usage: make <target> [BOARD=<board>] [CELL=<cellname>] [OPEN_ARGS=<options>]'
	@echo ''
	@echo 'Available targets:'
	@grep -hE '^[a-zA-Z0-9_.-]+:.*## .*$$' Makefile fpga.mk | awk 'BEGIN {FS = ":.*## "}; !seen[$$1]++ {printf "  %-20s %s\n", $$1, $$2}'
	@echo ''
	@echo 'BOARD selects the FPGA board and defaults to $(BOARD). Available: $(BOARDS).'
	@echo 'Every target except help, open and clean is forwarded to <BOARD>/Makefile.'
	@echo 'CELL defaults to the board Makefile TOP. Override to lint subcells.'
	@echo 'OPEN_ARGS passes extra options to sak-open.py for the open target (e.g. --all).'
.PHONY: help
# ================================================================================================


# Open Target
open: ## Open the design files of this folder in the sak-open.py file browser (needs the VNC/X11 desktop)
	sak-open.py $(OPEN_ARGS) .
.PHONY: open
# ================================================================================================


# Clean Target
# Cleans every board, not just $(BOARD), so `make clean` from the macro removes all build outputs.
clean: ## Remove the generated files of every board
	@for board in $(BOARDS); do $(MAKE) --no-print-directory -C $$board clean; done
.PHONY: clean
# ================================================================================================


# Everything else belongs to a board
%:
	@if [ ! -f $(BOARD)/Makefile ]; then \
		echo "Unknown BOARD '$(BOARD)'. Available: $(BOARDS)."; \
		exit 1; \
	fi
	@$(MAKE) -C $(BOARD) $@
