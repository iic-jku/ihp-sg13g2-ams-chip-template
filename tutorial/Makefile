# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

all: fig-pdf
	quarto render index.qmd

# Local Windows helper: the standalone rsvg-convert build ignores -o when Quarto passes -a, so pre-convert the SVG figures.
# Quarto reuses an existing fig/*.pdf instead of converting. The PDFs are gitignored, so CI still converts them itself with its own librsvg.
fig-pdf:
	for f in fig/*.svg; do \
		out="$${f%.svg}.pdf"; \
		if [ ! -f "$$out" ] || [ "$$f" -nt "$$out" ]; then \
			rsvg-convert -f pdf -o "$$out" "$$f"; \
		fi \
	done
.PHONY: fig-pdf

clean: ## Delete the rendered tutorial and the generated figure PDFs
	rm -rf .quarto _site index.pdf
	rm -f fig/*.pdf
.PHONY: clean

# Extra options for the sak-open.py file browser (e.g. --all to include build outputs)
# Override with: make open OPEN_ARGS=<options>
OPEN_ARGS ?=

open: ## Open the tutorial sources and figures in the sak-open.py file browser (needs the VNC/X11 desktop)
	sak-open.py $(OPEN_ARGS) .
.PHONY: open
