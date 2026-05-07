# SPDX-FileCopyrightText: 2025-2026 Simon Dorrer
# SPDX-License-Identifier: Apache-2.0

import os
import logging
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ClockCycles
from cocotb_tools.runner import get_runner

sim      = os.getenv("SIM", "icarus")
pdk_root = os.getenv("PDK_ROOT", Path("~/.ciel").expanduser())
pdk      = os.getenv("PDK", "ihp-sg13g2")
scl      = os.getenv("SCL", "sg13g2_stdcell")
gl       = os.getenv("GL", False)

hdl_toplevel = "counter_top"

# Defaults match counter_pkg::COUNTER_MAX_DEFAULT in rtl/constants.sv
COUNTER_MAX      = 15
COUNTER_BITWIDTH = (COUNTER_MAX + 1).bit_length() if COUNTER_MAX > 0 else 1
CLK_FREQ_MHZ     = 50


async def start_clock(clock, freq=CLK_FREQ_MHZ):
    """Start the clock @ freq MHz"""
    period_ns = round(1 / freq * 1000, 4)
    c = Clock(clock, period_ns, "ns")
    cocotb.start_soon(c.start())


async def reset(dut, cycles=2):
    """Pulse the active-low reset for `cycles` clock cycles."""
    cocotb.log.info("Reset asserted...")

    dut.reset_n_i.value = 0
    dut.enable_i.value  = 0
    await ClockCycles(dut.clock_i, cycles)
    dut.reset_n_i.value = 1
    await RisingEdge(dut.clock_i)

    cocotb.log.info("Reset deasserted.")


async def start_up(dut):
    """Startup sequence: clock + reset, counter disabled, value cleared."""
    await start_clock(dut.clock_i, CLK_FREQ_MHZ)
    await reset(dut)


@cocotb.test()
async def test_reset_clears_counter(dut):
    """After reset deasserts, counter_value_o must be zero."""
    logger = logging.getLogger("counter_tb")

    logger.info("Startup sequence...")
    await start_up(dut)

    assert int(dut.counter_value_o.value) == 0, \
        f"counter not zero after reset (got {int(dut.counter_value_o.value)})"

    logger.info("Done!")


@cocotb.test()
async def test_holds_when_disabled(dut):
    """With enable_i = 0, counter_value_o must not change."""
    logger = logging.getLogger("counter_tb")

    logger.info("Startup sequence...")
    await start_up(dut)

    dut.enable_i.value = 0
    await ClockCycles(dut.clock_i, 20)

    assert int(dut.counter_value_o.value) == 0, \
        f"counter changed while disabled (got {int(dut.counter_value_o.value)})"

    logger.info("Done!")


@cocotb.test()
async def test_increments_when_enabled(dut):
    """With enable_i = 1, counter_value_o must increment by 1 every clock."""
    logger = logging.getLogger("counter_tb")

    logger.info("Startup sequence...")
    await start_up(dut)

    dut.enable_i.value = 1

    # Sample on a few subsequent clock edges and verify monotonic +1
    expected = 0
    for _ in range(min(8, COUNTER_MAX + 1)):
        await RisingEdge(dut.clock_i)
        await Timer(1, "ns")  # let combinational settle past edge
        got = int(dut.counter_value_o.value)
        assert got == expected, f"expected {expected}, got {got}"
        expected += 1

    logger.info("Done!")


@cocotb.test()
async def test_wraps_at_max(dut):
    """Counter must wrap from COUNTER_MAX back to 0."""
    logger = logging.getLogger("counter_tb")

    logger.info("Startup sequence...")
    await start_up(dut)

    dut.enable_i.value = 1

    # Run long enough to hit COUNTER_MAX and wrap
    saw_max  = False
    saw_wrap = False
    prev     = 0
    for _ in range(2 * (COUNTER_MAX + 1) + 4):
        await RisingEdge(dut.clock_i)
        await Timer(1, "ns")
        cur = int(dut.counter_value_o.value)
        if cur == COUNTER_MAX:
            saw_max = True
        if saw_max and prev == COUNTER_MAX and cur == 0:
            saw_wrap = True
            break
        prev = cur

    assert saw_max,  "counter never reached COUNTER_MAX"
    assert saw_wrap, "counter did not wrap from COUNTER_MAX to 0"

    logger.info("Done!")


def counter_top_runner():

    proj_path = Path(__file__).resolve().parent

    sources  = []
    defines  = {}
    includes = [proj_path / "../../../rtl/"]

    if gl:
        # SCL models
        sources.append(Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / f"{scl}.v")
        sources.append(Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / "sg13g2_udp.v")

        # Unpowered gate-level netlist of the macro
        sources.append(proj_path / f"../../final/nl/{hdl_toplevel}.nl.v")

        defines = {"USE_POWER_PINS": False}
    else:
        sources.append(proj_path / "../../../rtl/constants.sv")
        sources.append(proj_path / "../../../rtl/counter.sv")
        sources.append(proj_path / "../../../rtl/counter_top.sv")

    build_args = []

    if sim == "icarus":
        build_args = ["-DSIM"]

    if sim == "verilator":
        build_args = ["--timing", "--trace", "--trace-fst", "--trace-structs"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel=hdl_toplevel,
        defines=defines,
        always=True,
        includes=includes,
        build_args=build_args,
        waves=True,
        timescale=("1ns", "1fs")
    )

    plusargs = []

    runner.test(
        hdl_toplevel=hdl_toplevel,
        test_module="counter_top_tb,",
        plusargs=plusargs,
        waves=True,
    )


if __name__ == "__main__":
    counter_top_runner()
