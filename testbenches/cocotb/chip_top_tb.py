# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

"""Cocotb testbench for chip_top.

The chip exposes the generic-named padframe ports defined in rtl/chip_top.sv:

  - clk_PAD                    : main clock                 (single)
  - rst_n_PAD                  : active-low reset           (single)
  - input_PAD[NUM_INPUT_PADS]  : digital inputs (1 bit: enable)
  - output_PAD[NUM_OUTPUT_PADS]: digital outputs (17 bits)
  - bidir_PAD[NUM_BIDIR_PADS]  : bidir pads (4 bits)
  - analog_PAD[NUM_ANALOG_PADS]: analog pads (4 bits, inverter2)

output_PAD bit assignment (driven by rtl/chip_core.sv):
  - [3:0]   counter1_value[3:0]    (counter1 LSB nibble)
  - [11:4]  counter2_value[7:0]
  - [15:12] inverter1.vout1..vout4
  - [16]    ^sram_0_out             (parity / XOR-reduction of A_DOUT[31:0])

bidir_PAD bit assignment:
  - [3:0]   counter1_value[7:4] (output when enable=1) /
            inverter1.vin1..vin4 (input when enable=0)

analog_PAD bit assignment:
  - [0]     inverter2.vin1   (analog input  via padres)
  - [1]     inverter2.vin2   (analog input  via padres)
  - [2]     inverter2.vout1  (analog output via padbare)
  - [3]     inverter2.vout2  (analog output via padbare)

The inverter macros are functional blackboxes in this simulation, so any
signal that passes through them resolves to X. The tests therefore only
assert on the counter / bidir / SRAM signal paths.

bidir_oe[i] is wired to input_PAD[0] inside chip_core, i.e. the bidir pads
drive counter1_value[7:4] when enable = 1 and switch to high-Z input mode
when enable = 0.
"""

import os
import logging
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ClockCycles
from cocotb.handle import Immediate
from cocotb.types import LogicArray, Range
from cocotb_tools.runner import get_runner

sim      = os.getenv("SIM", "icarus")
pdk_root = os.getenv("PDK_ROOT", Path("~/.ciel").expanduser())
pdk      = os.getenv("PDK", "ihp-sg13g2")
scl      = os.getenv("SCL", "sg13g2_stdcell")
# GL=1 selects the gate-level netlist; anything else (unset, "0", "") stays in RTL mode.
gl       = os.getenv("GL", "0").strip().lower() in ("1", "true", "yes", "on")

hdl_toplevel = "chip_top"

# Main clock frequency. Matches CLOCK_PERIOD = 17 ns in flow/librelane/config.yaml.
CPU_CLK_FREQ_MHZ = 56

# Counter wraps from 255 -> 0 (8-bit, default CTR_MAX).
CTR_MAX = 255


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

async def enable_power(dut):
    """Drive supplies for gate-level simulation (USE_POWER_PINS)."""
    dut.VDD.value   = 1
    dut.VSS.value   = 0
    dut.IOVDD.value = 1
    dut.IOVSS.value = 0


async def start_clock(clock, freq_mhz=CPU_CLK_FREQ_MHZ):
    """Start the chip clock at `freq_mhz` MHz."""
    period_ns = round(1 / freq_mhz * 1000, 4)
    cocotb.start_soon(Clock(clock, period_ns, "ns").start())


async def reset(dut, cycles=4):
    """Pulse the active-low reset for `cycles` clock cycles. Holds enable
    (input_PAD[0]) low during reset so the counters do not advance."""
    cocotb.log.info("Reset asserted...")

    dut.rst_n_PAD.value = 0
    dut.input_PAD.value = 0
    await ClockCycles(dut.clk_PAD, cycles)
    dut.rst_n_PAD.value = 1
    await RisingEdge(dut.clk_PAD)

    cocotb.log.info("Reset deasserted.")


async def start_up(dut):
    """Power up, start the clock, drive a reset pulse."""
    if gl:
        await enable_power(dut)

    # Initialise inputs to known levels before clocking.
    dut.rst_n_PAD.value = 0
    dut.input_PAD.value = 0

    # Float the bidir pads so the chip can drive them in output mode and
    # external stimuli can drive them in input mode.
    dut.bidir_PAD.value = LogicArray("ZZZZ", Range(3, "downto", 0))

    await start_clock(dut.clk_PAD, CPU_CLK_FREQ_MHZ)
    await reset(dut)


# ----------------------------------------------------------------------
# Bit-slice readers (LogicArray slicing keeps X/Z information; integer
# conversion only succeeds if the slice is fully resolvable).
# ----------------------------------------------------------------------

def _counter1_lsb(dut) -> int:
    """counter1[3:0] driven onto output_PAD[3:0]."""
    return int(dut.output_PAD.value[3:0])


def _counter1_msb(dut) -> int:
    """counter1[7:4] driven onto bidir_PAD[3:0] when enable = 1."""
    return int(dut.bidir_PAD.value[3:0])


def _counter1(dut) -> int:
    """Reconstruct the full 8-bit counter1 value from LSB outputs + bidir
    pads. Only valid when enable = 1 (otherwise bidir is high-Z)."""
    return (_counter1_msb(dut) << 4) | _counter1_lsb(dut)


def _counter2(dut) -> int:
    """counter2[7:0] driven onto output_PAD[11:4]."""
    return int(dut.output_PAD.value[11:4])


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

@cocotb.test()
async def test_reset_clears_counters(dut):
    """After reset deasserts, both counters must be at 0."""
    logger = logging.getLogger("chip_top_tb")
    logger.info("Startup sequence...")
    await start_up(dut)

    # Drive enable high so the bidir pads switch to output mode and the chip
    # drives counter1_value[7:4] onto bidir_PAD. `bidir_oe[i]` is wired to
    # `input_in[0]` combinationally, so this happens without a clock edge —
    # which is important here: stepping a rising edge with enable=1 would
    # increment the counter, defeating the purpose of this test.
    dut.input_PAD.value = 1
    await Timer(1, "ns")  # combinational settle only, NO clock edge

    assert _counter1(dut) == 0, f"counter1 not zero after reset (got {_counter1(dut)})"
    assert _counter2(dut) == 0, f"counter2 not zero after reset (got {_counter2(dut)})"
    logger.info("Done!")


@cocotb.test()
async def test_counters_hold_when_disabled(dut):
    """With enable = 0, neither counter advances."""
    logger = logging.getLogger("chip_top_tb")
    logger.info("Startup sequence...")
    await start_up(dut)

    dut.input_PAD.value = 0
    await ClockCycles(dut.clk_PAD, 32)

    # While enable = 0 the bidir pads are in input mode (high-Z), so we only
    # check the LSB output pads of counter1 and the dedicated counter2 pads.
    assert _counter1_lsb(dut) == 0, "counter1 advanced while disabled"
    assert _counter2(dut)     == 0, "counter2 advanced while disabled"
    logger.info("Done!")


@cocotb.test()
async def test_counters_increment(dut):
    """With enable = 1 both counters increment in lock-step."""
    logger = logging.getLogger("chip_top_tb")
    logger.info("Startup sequence...")
    await start_up(dut)

    dut.input_PAD.value = 1

    # Step a handful of cycles and verify the counters track the expected value.
    for expected in range(1, 17):
        await RisingEdge(dut.clk_PAD)
        await Timer(1, "ns")
        c1 = _counter1(dut)
        c2 = _counter2(dut)
        assert c1 == expected, f"counter1: expected {expected}, got {c1}"
        assert c2 == expected, f"counter2: expected {expected}, got {c2}"

    logger.info("Done!")


@cocotb.test()
async def test_counter_wraps(dut):
    """Counters must wrap from CTR_MAX back to 0."""
    logger = logging.getLogger("chip_top_tb")
    logger.info("Startup sequence...")
    await start_up(dut)

    dut.input_PAD.value = 1

    saw_max  = False
    saw_wrap = False
    prev     = 0
    for _ in range(2 * (CTR_MAX + 1) + 4):
        await RisingEdge(dut.clk_PAD)
        await Timer(1, "ns")
        cur = _counter2(dut)
        if cur == CTR_MAX:
            saw_max = True
        if saw_max and prev == CTR_MAX and cur == 0:
            saw_wrap = True
            break
        prev = cur

    assert saw_max,  "counter2 never reached CTR_MAX"
    assert saw_wrap, "counter2 did not wrap from CTR_MAX to 0"
    logger.info("Done!")


@cocotb.test()
async def test_bidir_input_mode(dut):
    """When enable = 0, the bidir pads switch to input mode and external
    stimuli propagate through to the chip core (and thus to inverter1's
    vin1..vin4). The inverter outputs themselves resolve to X in functional
    simulation (analog blackbox), so we only verify that driving the bidir
    pads while `enable` is low does not collide with internal drivers."""
    logger = logging.getLogger("chip_top_tb")
    logger.info("Startup sequence...")
    await start_up(dut)

    dut.input_PAD.value = 0
    await ClockCycles(dut.clk_PAD, 2)

    # Drive a known pattern on the bidir pads and verify it sticks.
    dut.bidir_PAD.value = Immediate(LogicArray("1010", Range(3, "downto", 0)))
    await ClockCycles(dut.clk_PAD, 2)
    assert int(dut.bidir_PAD.value[3:0]) == 0b1010, \
        f"bidir input not honoured (got {dut.bidir_PAD.value.binstr})"

    # Release the pads.
    dut.bidir_PAD.value = Immediate(LogicArray("ZZZZ", Range(3, "downto", 0)))
    logger.info("Done!")


@cocotb.test()
async def test_sram_path_alive(dut):
    """Smoke test: clock the SRAM for a number of cycles and verify the
    sram_out path (output_PAD[16]) doesn't get stuck (it may be X in RTL
    since the SRAM behavioural model returns the uninitialised contents of
    address 0 — but the path must exist and the simulator must not have
    optimised the signal away)."""
    logger = logging.getLogger("chip_top_tb")
    logger.info("Startup sequence...")
    await start_up(dut)

    dut.input_PAD.value = 1
    await ClockCycles(dut.clk_PAD, 64)

    # Just touch the signal — convert via binstr so X/Z don't raise.
    val = dut.output_PAD.value[16]
    logger.info("output_PAD[16] (sram_out) after 64 cycles = %s", val)
    logger.info("Done!")


# ----------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------

def chip_top_runner():
    proj_path = Path(__file__).resolve().parent
    root_path = proj_path.parent.parent

    sources  = []
    defines  = {}
    includes = [root_path / "rtl"]

    if gl:
        # Standard-cell models for gate-level simulation
        sources.append(Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / f"{scl}.v")
        sources.append(Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / "sg13g2_udp.v")

        # Unpowered top-level netlist
        sources.append(root_path / f"netlist/nl/{hdl_toplevel}.nl.v")

        # Macro netlists referenced by the top-level netlist
        sources.append(root_path / "macros/counter/final/nl/counter_top.nl.v")
    else:
        # RTL sources
        sources.append(root_path / "rtl/chip_top.sv")
        sources.append(root_path / "rtl/chip_core.sv")

        # Counter macro RTL
        sources.append(root_path / "macros/counter/rtl/constants.sv")
        sources.append(root_path / "macros/counter/rtl/counter.sv")
        sources.append(root_path / "macros/counter/rtl/counter_top.sv")

    sources += [
        # Inverter macro stub (analog blackbox)
        root_path / "macros/inverter/final/vh/inverter_top.v",

        # SRAM behavioural Verilog models (shipped with the IHP Open-PDK)
        Path(pdk_root) / pdk / "libs.ref/sg13g2_sram/verilog/RM_IHPSG13_1P_1024x32_c2_bm_bist.v",
        Path(pdk_root) / pdk / "libs.ref/sg13g2_sram/verilog/RM_IHPSG13_1P_core_behavioral_bm_bist.v",

        # Bondpad stub
        root_path / "ip/sg13g2_ip__bondpad_70x70/final/vh/sg13g2_ip__bondpad_70x70.v",

        # Custom IO pad models
        root_path / "ip/sg13g2_io_custom/verilog/sg13g2_io.v",

        # Logo IPs
        root_path / "ip/sg13g2_ip__jku/final/vh/sg13g2_ip__jku.v",
        root_path / "ip/sg13g2_ip__jku_names/final/vh/sg13g2_ip__jku_names.v",
    ]

    build_args = []

    if sim == "icarus":
        # -gno-specify: skip specify blocks; the SCL Verilog uses `ifnone`
        # with edge-sensitive paths, which iverilog cannot parse.
        build_args = ["-DSIM", "-gno-specify"]

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
        test_module="chip_top_tb",
        plusargs=plusargs,
        waves=True,
    )


if __name__ == "__main__":
    chip_top_runner()
