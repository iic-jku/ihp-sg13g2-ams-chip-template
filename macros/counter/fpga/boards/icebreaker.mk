# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

ARCH         := ice40
ICE40_DEVICE := --up5k --package sg48

# openFPGALoader has no dedicated iCEBreaker board profile.
# Must be `=`, not `:=`, since BITSTREAM is only defined later, by fpga.mk.
LOAD_CMD  = iceprog -S $(BITSTREAM)
FLASH_CMD = iceprog $(BITSTREAM)
