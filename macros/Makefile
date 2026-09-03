# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.DEFAULT_GOAL := help

# Folder structure
SCRIPTS_DIR := scripts

# Every folder with a Makefile is a macro
MACROS := $(sort $(patsubst %/,%,$(dir $(wildcard */Makefile))))

# The macro to copy and the name of the new one
# Usage: make macro FROM=<macro> NAME=<name>
FROM := $(patsubst %/,%,$(FROM))
NAME := $(patsubst %/,%,$(NAME))

# Both names in their three spellings (inverter, Inverter, INVERTER): file names, file contents and GDS cell names are replaced in all three
_FROM_TITLE := $(shell echo '$(FROM)' | sed 's/./\U&/')
_FROM_UPPER := $(shell echo '$(FROM)' | tr a-z A-Z)
_NAME_TITLE := $(shell echo '$(NAME)' | sed 's/./\U&/')
_NAME_UPPER := $(shell echo '$(NAME)' | tr a-z A-Z)
_FROM_ANY   := -e '$(FROM)' -e '$(_FROM_TITLE)' -e '$(_FROM_UPPER)'
_RENAME     := -e 's/$(FROM)/$(NAME)/g' -e 's/$(_FROM_TITLE)/$(_NAME_TITLE)/g' -e 's/$(_FROM_UPPER)/$(_NAME_UPPER)/g'

# Files that describe the copied design rather than reference it: the replace pass leaves them to the designer
_KEEP := --exclude=README.md --exclude='*.ipynb'


# Help Target
help: ## Show this help message
	@echo 'Usage: make <target> [FROM=<macro>] [NAME=<name>]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z0-9_.-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ''
	@echo 'FROM selects the macro to copy. Available: $(MACROS).'
	@echo 'NAME names the new macro: a lowercase letter followed by lowercase letters, digits or underscores.'
.PHONY: help
# ================================================================================================


# Macro Target
macro: ## Start a new macro as a renamed copy of an existing one (usage: make macro FROM=<macro> NAME=<name>)
	@test -n '$(FROM)' || { echo "Set FROM to the macro to copy. Available: $(MACROS)."; exit 1; }
	@test -f '$(FROM)/Makefile' || { echo "Unknown macro '$(FROM)'. Available: $(MACROS)."; exit 1; }
	@echo '$(FROM)' | grep -Eq '^[a-z][a-z0-9_]*$$' || { echo "FROM '$(FROM)' is not a lowercase identifier, the rename would not be exact."; exit 1; }
	@test -n '$(NAME)' || { echo "Set NAME to the name of the new macro."; exit 1; }
	@echo '$(NAME)' | grep -Eq '^[a-z][a-z0-9_]*$$' || { echo "NAME '$(NAME)' must be a lowercase letter followed by lowercase letters, digits or underscores."; exit 1; }
	@test '$(NAME)' != '$(FROM)' || { echo "NAME must differ from FROM."; exit 1; }
	@test ! -e '$(NAME)' || { echo "'$(NAME)' exists already, remove it or pick another NAME."; exit 1; }
	@echo "Copying $(FROM)/ to $(NAME)/ ..."
	@mkdir -p $(NAME)
	@if git -C $(FROM) rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		cd $(FROM) && git ls-files --cached --others --exclude-standard -z | xargs -0 cp --parents -t $(MAKEFILE_DIR)/$(NAME); \
	else \
		echo "$(FROM)/ is not inside a git checkout, copying every file including the build outputs"; \
		cp -r $(FROM)/. $(NAME)/; \
	fi
	@echo "Removing the build outputs of $(FROM) ..."
	@$(MAKE) --no-print-directory -C $(NAME) clean >/dev/null
	@echo "Renaming the files and folders ..."
	@find $(NAME) -mindepth 1 -depth \( -name '*$(FROM)*' -o -name '*$(_FROM_TITLE)*' -o -name '*$(_FROM_UPPER)*' \) | while IFS= read -r f; do \
		mv "$$f" "$$(dirname "$$f")/$$(basename "$$f" | sed $(_RENAME))"; \
	done
	@echo "Replacing $(FROM), $(_FROM_TITLE) and $(_FROM_UPPER) inside the files ..."
	@grep -rIlZ $(_KEEP) $(_FROM_ANY) $(NAME) | xargs -0 -r sed -i $(_RENAME)
	@if ls $(NAME)/layout/*.gds >/dev/null 2>&1; then \
		echo "Renaming the cells inside the GDS files ..."; \
		for gds in $$(ls $(NAME)/layout/*.gds | grep -v '\.klay\.gds$$') $$(ls $(NAME)/layout/*.klay.gds 2>/dev/null); do \
			klayout -z -nc -r $(SCRIPTS_DIR)/rename_gds_cells.py -rd gds=$$gds -rd old=$(FROM) -rd new=$(NAME) || exit 1; \
		done; \
	fi
	@echo ''
	@echo "Left untouched, they describe the $(FROM) design (adapt or delete them):"
	@grep -rIl --include=README.md --include='*.ipynb' $(_FROM_ANY) $(NAME) | sed 's/^/  /' | grep . || echo '  none'
	@echo "Still carrying '$(FROM)' after the rename:"
	@left=$$( if echo '$(NAME)' | grep -q '$(FROM)'; then \
			grep -rIl $(_KEEP) $(_FROM_ANY) $(NAME) | while IFS= read -r f; do \
				sed -e 's/$(NAME)//g' -e 's/$(_NAME_TITLE)//g' -e 's/$(_NAME_UPPER)//g' "$$f" | grep -q $(_FROM_ANY) && echo "  $$f"; \
			done; \
		else \
			grep -rIl $(_KEEP) $(_FROM_ANY) $(NAME) | sed 's/^/  /'; \
		fi; true ); \
	echo "$${left:-  none}"
	@echo ''
	@echo "$(NAME)/ is a renamed copy of $(FROM)/ and builds as one. See README.md in this folder for what to replace next and where to register the macro at the chip top-level."
.PHONY: macro
# ================================================================================================
