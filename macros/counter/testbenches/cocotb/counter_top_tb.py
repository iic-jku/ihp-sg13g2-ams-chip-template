# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: cocotb testbench for counter_top with a driver, a monitor, a reference model, a scoreboard, and functional coverage, built like the testbenches of the VLSI design course.
# Environment variables: SIM selects the simulator (default icarus). GL=1 (Icarus only) simulates the netlist final/nl/counter_top.nl.v of the macro, SDF=1 adds the delays of the SDF file of SDF_CORNER, and SDF_TRIPLE selects the min, typ or max value of each delay.
# CLK_PERIOD_NS sets the clock (default from rtl/constants.sv), and CHECK=0 switches the scoreboard checks off.

import os
import random
import re
from collections import Counter
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, ReadOnly
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
    text = _CONSTANTS_SV.read_text(encoding="utf-8")
    m = re.search(rf"^\s*`define\s+{re.escape(name)}\s+(\S+)", text, re.MULTILINE)
    if m is None:
        raise RuntimeError(f"`{name} not found in {_CONSTANTS_SV}")
    return m.group(1)


CTR_MAX       = int(_read_define("COUNTER_MAX_DEFAULT"))
CLK_PERIOD_NS = float(os.getenv("CLK_PERIOD_NS", 1e9 / float(_read_define("CLK_FREQ_DEFAULT"))))
CHECK         = os.getenv("CHECK", "1") == "1"


class Scoreboard:
    """Reference model of the specification, checks, and coverage."""

    def __init__(self):
        self.value = 0  # model of counter_value_o
        self.coverage = Counter()

    def check(self, value):
        """Compare the output of the DUT with the model."""
        assert value == self.value, f"counter_value_o = {value}, expected {self.value}"

    def update(self, reset_n, enable):
        """Count coverage, then apply one clock edge to the model."""
        state = "zero" if self.value == 0 else "max" if self.value == CTR_MAX else "between"
        op = "reset" if not reset_n else "count" if enable else "hold"
        self.coverage[f"{op} at {state}"] += 1
        if not reset_n:  # the synchronous reset wins over enable_i
            self.value = 0
        elif enable:  # wraps from CTR_MAX to 0
            self.value = 0 if self.value == CTR_MAX else self.value + 1


async def monitor(dut, sb):
    """Sample the DUT at every falling edge, after the driver."""
    while True:
        await ReadOnly()
        if CHECK:
            sb.check(dut.counter_value_o.value)
        sb.update(int(dut.reset_n_i.value), int(dut.enable_i.value))
        await FallingEdge(dut.clock_i)


async def driver(dut, transactions):
    """Apply one (reset_n, enable) transaction per clock cycle."""
    for reset_n, enable in transactions:
        dut.reset_n_i.value = reset_n
        dut.enable_i.value = enable
        await FallingEdge(dut.clock_i)
    dut.reset_n_i.value = 1
    dut.enable_i.value = 0
    await ClockCycles(dut.clock_i, 2)


async def start_up(dut):
    """Start the clock, reset the DUT, and start the monitor."""
    cocotb.start_soon(Clock(dut.clock_i, CLK_PERIOD_NS, "ns").start())
    dut.reset_n_i.value = 0
    dut.enable_i.value = 0
    await ClockCycles(dut.clock_i, 2)
    # The inputs change at the falling edge, so that they cannot race the clock tree of the timed netlist
    await FallingEdge(dut.clock_i)
    dut.reset_n_i.value = 1
    sb = Scoreboard()
    cocotb.start_soon(monitor(dut, sb))
    return sb


def report(sb):
    """Log the coverage bins, return the bins that were never hit."""
    bins = [f"{op} at {state}"
            for op in ("reset", "hold", "count")
            for state in ("zero", "between", "max")]
    for name in bins:
        cocotb.log.info(f"{name:16s} {sb.coverage[name]:5d}")
    return [name for name in bins if sb.coverage[name] == 0]


@cocotb.test()
async def test_reset_clears_counter(dut):
    """Directed: count to 10, reset while enabled, count again."""
    sb = await start_up(dut)
    await driver(dut, [(1, 1)] * 10 + [(0, 1)] * 2 + [(1, 1)] * 5)
    report(sb)


@cocotb.test()
async def test_holds_when_disabled(dut):
    """Directed: hold at zero, count to 5, hold there."""
    sb = await start_up(dut)
    await driver(dut, [(1, 0)] * 5 + [(1, 1)] * 5 + [(1, 0)] * 20)
    report(sb)


@cocotb.test()
async def test_increments_when_enabled(dut):
    """Directed: increment by one in every cycle."""
    sb = await start_up(dut)
    await driver(dut, [(1, 1)] * 16)
    report(sb)


@cocotb.test()
async def test_wraps_at_max(dut):
    """Directed: count to CTR_MAX, hold there, wrap to 0, count to CTR_MAX again and reset there."""
    sb = await start_up(dut)
    await driver(dut, [(1, 1)] * CTR_MAX + [(1, 0)] * 3 + [(1, 1)] * (CTR_MAX + 1) + [(0, 1)])
    report(sb)


@cocotb.test()
async def test_random(dut):
    """Random: rounds of a reset, a run to a random value or to CTR_MAX, and random operations."""
    sb = await start_up(dut)
    transactions = []
    for _ in range(40):
        # Half of the runs stop at CTR_MAX, which plain random stimulus would rarely reach
        run = random.choice([random.randrange(CTR_MAX), CTR_MAX])
        transactions += [(0, 0)] + [(1, 1)] * run
        for _ in range(20):
            transactions.append((int(random.random() >= 0.2), int(random.random() < 0.5)))
    await driver(dut, transactions)
    holes = report(sb)
    assert not holes, f"coverage holes: {holes}"


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
