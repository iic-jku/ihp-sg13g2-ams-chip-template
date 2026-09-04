# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

all: fig-pdf
	quarto render index.qmd

# Local Windows helper: the standalone rsvg-convert build ignores -o when Quarto passes -a, so pre-convert the SVG figures.
# Quarto reuses an existing <name>.pdf next to <name>.svg instead of converting it itself, and CI converts them with its own librsvg.
# Every figure lives in a per-topic subfolder, so the search recurses. A figure PDF that git tracks is left alone: those are draw.io
# exports committed next to their SVG, and regenerating them from the SVG only dirties the tree.
fig-pdf:
	find fig -name '*.svg' | while read -r f; do \
		out="$${f%.svg}.pdf"; \
		if git ls-files --error-unmatch "$$out" >/dev/null 2>&1; then continue; fi; \
		if [ ! -f "$$out" ] || [ "$$f" -nt "$$out" ]; then \
			rsvg-convert -f pdf -o "$$out" "$$f"; \
		fi \
	done
.PHONY: fig-pdf

clean: ## Delete the rendered tutorial and the generated figure PDFs
	rm -rf .quarto _site index.pdf
	find fig -name '*.pdf' | while read -r p; do \
		git ls-files --error-unmatch "$$p" >/dev/null 2>&1 || rm -f "$$p"; \
	done
.PHONY: clean

# Extra options for the sak-open.py file browser (e.g. --all to include build outputs)
# Override with: make open OPEN_ARGS=<options>
OPEN_ARGS ?=

open: ## Open the tutorial sources and figures in the sak-open.py file browser (needs the VNC/X11 desktop)
	sak-open.py $(OPEN_ARGS) .
.PHONY: open
