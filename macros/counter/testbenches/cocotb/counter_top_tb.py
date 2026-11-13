# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

import os
import re
import logging
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles
from cocotb_tools.runner import get_results, get_runner

sim      = os.getenv("SIM", "icarus")
pdk_root = os.getenv("PDK_ROOT", Path("~/.ciel").expanduser())
pdk      = os.getenv("PDK", "ihp-sg13g2")
scl      = os.getenv("SCL", "sg13g2_stdcell")
# GL=1 selects the gate-level netlist; anything else (unset, "0", "") stays in RTL mode.
gl       = os.getenv("GL", "0").strip().lower() in ("1", "true", "yes", "on")
# SDF=1 adds the delays of the SDF file of SDF_CORNER to the netlist, SDF_TRIPLE selects the min, typ or max value of each delay.
sdf        = os.getenv("SDF", "0").strip().lower() in ("1", "true", "yes", "on")
sdf_corner = os.getenv("SDF_CORNER", "nom_typ_1p50V_25C")
sdf_triple = os.getenv("SDF_TRIPLE", "typ")

hdl_toplevel = "counter_top"

# Defaults sourced from rtl/constants.sv, the single source of truth shared with the SV testbench and the DUT.
_CONSTANTS_SV = Path(__file__).resolve().parent / "../../rtl/constants.sv"


def _read_define(name: str) -> str:
    """Extract the value of a `define <name> <value>` macro from rtl/constants.sv."""
    text = _CONSTANTS_SV.read_text()
    m = re.search(rf"^\s*`define\s+{re.escape(name)}\s+(\S+)", text, re.MULTILINE)
    if m is None:
        raise RuntimeError(f"`{name} not found in {_CONSTANTS_SV}")
    return m.group(1)


CTR_MAX      = int(_read_define("COUNTER_MAX_DEFAULT"))
CLK_FREQ_HZ      = float(_read_define("CLK_FREQ_DEFAULT"))
CLK_FREQ_MHZ     = int(CLK_FREQ_HZ / 1e6)
CTR_BW = (CTR_MAX + 1).bit_length() if CTR_MAX > 0 else 1


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
    # Change the inputs at the falling edge, so that they cannot race the clock tree of the timed netlist
    await FallingEdge(dut.clock_i)
    dut.reset_n_i.value = 1
    await FallingEdge(dut.clock_i)

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
    expected = 1
    for _ in range(min(8, CTR_MAX + 1)):
        await RisingEdge(dut.clock_i)
        await FallingEdge(dut.clock_i)  # sample half a period after the edge
        got = int(dut.counter_value_o.value)
        assert got == expected, f"expected {expected}, got {got}"
        expected += 1

    logger.info("Done!")


@cocotb.test()
async def test_wraps_at_max(dut):
    """Counter must wrap from CTR_MAX back to 0."""
    logger = logging.getLogger("counter_tb")

    logger.info("Startup sequence...")
    await start_up(dut)

    dut.enable_i.value = 1

    # Run long enough to hit CTR_MAX and wrap
    saw_max  = False
    saw_wrap = False
    prev     = 0
    for _ in range(2 * (CTR_MAX + 1) + 4):
        await RisingEdge(dut.clock_i)
        await FallingEdge(dut.clock_i)
        cur = int(dut.counter_value_o.value)
        if cur == CTR_MAX:
            saw_max = True
        if saw_max and prev == CTR_MAX and cur == 0:
            saw_wrap = True
            break
        prev = cur

    assert saw_max,  "counter never reached CTR_MAX"
    assert saw_wrap, "counter did not wrap from CTR_MAX to 0"

    logger.info("Done!")


def counter_top_runner():

    proj_path = Path(__file__).resolve().parent

    sources  = []
    defines  = {}
    includes = [proj_path / "../../rtl/"]

    if gl:
        # SCL models
        sources.append(Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / f"{scl}.v")
        sources.append(Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / "sg13g2_udp.v")

        # Unpowered gate-level netlist of the macro
        sources.append(proj_path / f"../../final/nl/{hdl_toplevel}.nl.v")

        # Unpowered netlist: USE_POWER_PINS must NOT be defined at all
        # (passing USE_POWER_PINS=False would still define the macro).
    else:
        sources.append(proj_path / "../../rtl/constants.sv")
        sources.append(proj_path / "../../rtl/counter.sv")
        sources.append(proj_path / "../../rtl/counter_top.sv")

    toplevel   = hdl_toplevel
    build_args = []
    plusargs   = []

    if sim == "icarus":
        # -gno-specify: ignore the specify blocks, so every cell switches without delay.
        build_args = ["-DSIM", "-gno-specify"]

    if gl and sdf:
        if sim != "icarus":
            raise SystemExit("The timed gate-level simulation (SDF=1) needs SIM=icarus.")
        sdf_file = proj_path / f"../../final/sdf/{sdf_corner}/{hdl_toplevel}__{sdf_corner}.sdf"
        if not sdf_file.is_file():
            raise SystemExit(f"No SDF file {sdf_file} found. Run 'make build-top' (or 'make copy-final') first.")
        # The wrapper instantiates the netlist and annotates the SDF file. -gspecify keeps the delays of the cell
        # models, -ginterconnect the wire delays of the layout, and -T selects the value of each min:typ:max delay.
        toplevel   = f"{hdl_toplevel}_sdf"
        sources   += [proj_path / "../../rtl/constants.sv", proj_path / f"{toplevel}.sv"]
        build_args = ["-DSIM", "-gspecify", "-ginterconnect", f"-T{sdf_triple}"]
        plusargs   = [f"+SDF={sdf_file.resolve()}"]

    if sim == "verilator":
        build_args = ["--timing", "--trace", "--trace-fst", "--trace-structs"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel=toplevel,
        defines=defines,
        always=True,
        includes=includes,
        build_args=build_args,
        waves=True,
        timescale=("1ns", "1fs")
    )

    results_xml = runner.test(
        hdl_toplevel=toplevel,
        test_module="counter_top_tb",
        plusargs=plusargs,
        waves=True,
    )

    # Outside pytest a failing test leaves the exit status at 0, so check the results
    num_tests, num_failed = get_results(results_xml)
    if num_failed:
        raise SystemExit(f"FAIL: {num_failed} of {num_tests} tests failed")


if __name__ == "__main__":
    counter_top_runner()
