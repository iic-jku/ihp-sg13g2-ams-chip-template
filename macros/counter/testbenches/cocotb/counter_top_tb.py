# SPDX-FileCopyrightText: 2025-2026 The Chip Team
# SPDX-License-Identifier: Apache-2.0

import os
import logging
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, Edge, RisingEdge, FallingEdge, ClockCycles
from cocotb.handle import Immediate
from cocotb.types import LogicArray, Logic, Range
from cocotb_tools.runner import get_runner

sim = os.getenv("SIM", "icarus")
pdk_root = os.getenv("PDK_ROOT", Path("~/.ciel").expanduser())
pdk = os.getenv("PDK", "ihp-sg13g2")
scl = os.getenv("SCL", "sg13g2_stdcell")
gl = os.getenv("GL", False)

hdl_toplevel = "counter_top"

CPU_CLK_FREQ = 56  # MHz

mem = {}
async def set_defaults(dut, program_path):
    global mem
    mem = {}

    lines = ()
    with open(program_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        mem[i] = LogicArray(int(line, base=16), Range(7, "downto", 0))


async def start_clock(clock, freq=20):
    """Start the clock @ freq MHz"""
    inverted = round(1 / freq * 1000, 4)
    c = Clock(clock, inverted, "ns")
    cocotb.start_soon(c.start())


async def reset(reset, active_low=True, time_ns=1000):
    """Reset dut"""
    cocotb.log.info("Reset asserted...")

    reset.value = not active_low
    await Timer(time_ns, "ns")
    reset.value = active_low

    cocotb.log.info("Reset deasserted.")


async def start_up(dut, program_path):
    global CPU_CLK_FREQ
    """Startup sequence"""
    await set_defaults(dut, program_path)
    await start_clock(dut.clk, CPU_CLK_FREQ)
    await reset(dut.reset)

state = "RECV_COMMAND"
WRITE_CMD = 2
READ_CMD = 3
command_reg = LogicArray(0, Range(7, "downto", 0))
addr_reg = LogicArray(0, Range(23, "downto", 0))
datain_reg = LogicArray(0, Range(7, "downto", 0))
dataout_reg = LogicArray(0, Range(7, "downto", 0))
index = 0
mem_pattern = []
prev_sclk = 0


async def do_spi(dut):
    global state
    global mem
    global WRITE_CMD
    global READ_CMD
    global command_reg
    global addr_reg
    global datain_reg
    global dataout_reg
    global index
    global mem_pattern
    global prev_sclk

    sclk = dut.sclk.get()
    si = dut.si.get()
    if dut.sram_ce.get() == 0:  # cs = 0
        state = "RECV_COMMAND"
        index = 7
        prev_sclk = sclk
        dut.so.set(Immediate(Logic(0)))

        return

    if sclk == 1 and prev_sclk == 0:
        if state == "RECV_COMMAND":
            if dut.sram_ce.get() == 1:
                command_reg[index] = si
                if index == 0:
                    index = 23
                    state = "RECV_ADDR"
                else:
                    index = index - 1

        elif state == "RECV_ADDR":
            addr_reg[index] = si
            if index == 0:
                index = 7

                # print(f"Current: {hex(addr_reg)}")
                if command_reg.to_unsigned() == READ_CMD:
                    state = "SEND_DATA"
                    addr_tmp = addr_reg[22:0].to_unsigned()
                    dataout_reg = mem[addr_tmp]

                elif command_reg.to_unsigned() == WRITE_CMD:
                    state = "RECV_DATA"
                    index = 7
                else:
                    print("GOT UNKNOWN SPI COMMAND!!!!!")
            else:
                index = index - 1

        elif state == "WAITING":
            state = "SEND_DATA"

        elif state == "RECV_DATA":
            datain_reg[index] = si
            if index == 0:
                mem[addr_reg.to_unsigned()] = LogicArray(datain_reg.to_unsigned(), Range(7, "downto", 0))

                mem_pattern.append((addr_reg[22:0].to_unsigned(), datain_reg.to_unsigned()))
                index = 7
                addr_reg = LogicArray(addr_reg[22:0].to_unsigned() + 1, Range(23, "downto", 0))
            else:
                index = index - 1

        elif state == "SEND_DATA":
            if index == 0:
                index = 7
                addr_reg = LogicArray(addr_reg[22:0].to_unsigned() + 1, Range(23, "downto", 0))
                addr_tmp = addr_reg.to_unsigned()
                if addr_tmp in mem:
                    dataout_reg = mem[addr_reg.to_unsigned()]
                else:
                    dataout_reg = LogicArray("XXXXXXXX", Range(7, "downto", 0))
            else:
                index = index - 1

    elif sclk == 0 and prev_sclk == 1:
        if state == "SEND_DATA":
            dut.so.set(Immediate(dataout_reg[index]))

    prev_sclk = sclk


uart_rx_bytes = list()  # List of bytes sent by the CPU to the tb
UART_RX_BAUD = 115200
# UART_RX_WAIT_CYCLES = (1e9 * (1.0 / UART_RX_BAUD)) / (1e3 * (1.0 / CPU_CLK_FREQ))
UART_RX_WAIT_CYCLES = 510
uart_rx_clk_counter = 0
uart_rx_bit_counter = 0
uart_rx_state = "IDLE"  # IDLE, WAIITNG, RECV
uart_rx_current_data = 0


async def do_uart_rx(dut):
    global uart_rx_bytes
    global UART_RX_WAIT_CYCLES
    global uart_rx_clk_counter
    global uart_rx_bit_counter
    global uart_rx_state
    global uart_rx_current_data

    cpu_tx = dut.tx.get()

    if uart_rx_state == "IDLE":
        if cpu_tx == 1:
            # No start condition. Doing nothing
            return

        uart_rx_state = "RECV"
        uart_rx_clk_counter = 1.5 * UART_RX_WAIT_CYCLES
        uart_rx_bit_counter = 0
        uart_rx_current_data = LogicArray(0, Range(7, "downto", 0))

    elif uart_rx_state == "RECV":
        uart_rx_clk_counter -= 1

        if uart_rx_clk_counter != 0:
            return

        uart_rx_clk_counter = UART_RX_WAIT_CYCLES
        if uart_rx_bit_counter <= 7:
            uart_rx_current_data[uart_rx_bit_counter] = cpu_tx
            uart_rx_bit_counter += 1
        else:
            if cpu_tx == 0:
                print("Expected to see UART stop condition on rx!")
            else:
                uart_rx_state = "IDLE"
                uart_rx_bytes.append(chr(uart_rx_current_data.to_unsigned()))


UART_TX_BAUD = 115200
# UART_TX_WAIT_CYCLES = (1e9 * (1.0 / UART_RX_BAUD)) / (1e3 * (1.0 / CPU_CLK_FREQ))
UART_TX_WAIT_CYCLES = 510
uart_tx_clk_counter = 0
uart_tx_bit_counter = 0
uart_tx_state = "IDLE"  # IDLE, TX, END
uart_tx_current_data = 0
uart_tx_enable = 0


async def do_uart_tx(dut):
    global UART_TX_WAIT_CYCLES
    global uart_tx_clk_counter
    global uart_tx_bit_counter
    global uart_tx_state
    global uart_tx_current_data
    global uart_tx_enable

    if uart_tx_enable == 0:
        return

    cpu_rx_in = 1

    if uart_tx_state == "IDLE":
        cpu_rx_in = 0

        uart_tx_state = "TX"
        uart_tx_clk_counter = 1 * UART_TX_WAIT_CYCLES
        uart_tx_bit_counter = 0

    elif uart_tx_state == "TX":
        uart_tx_clk_counter -= 1

        if uart_tx_clk_counter != 0:
            return

        uart_tx_clk_counter = UART_TX_WAIT_CYCLES
        if uart_tx_bit_counter <= 7:
            cpu_rx_in = uart_tx_current_data[uart_tx_bit_counter]
            uart_tx_bit_counter += 1
        else:
            uart_tx_state = "IDLE"
            cpu_rx_in = 1
            uart_tx_enable = 0

    # Set CPU rx input to the computed value
    dut.rx.set(Immediate(cpu_rx_in))


i2c_state = "IDLE"
prev_scl = 1
prev_sda = 1
i2c_addr = 0
i2c_cmd = 0
i2c_counter = 0
i2c_index = 3
i2c_recv = []
i2c_current_recv = LogicArray(0, Range(7, "downto", 0))
async def do_i2c_slave(dut):
    global i2c_state
    global prev_scl
    global i2c_addr
    global i2c_cmd
    global i2c_counter
    global i2c_index
    global i2c_recv
    global i2c_current_recv
    global prev_sda

    # Some random values
    i2c_send = [
        LogicArray(37, Range(7, "downto", 0)),
        LogicArray(29, Range(7, "downto", 0)),
        LogicArray(204, Range(7, "downto", 0)),
        LogicArray(103, Range(7, "downto", 0))
    ]

    sda_in = dut.sda_o.get()
    scl = dut.scl.get()

    # if scl == 1 and prev_scl == 1 and sda_in == 1 and prev_sda == 0:
    if scl == 1 and prev_scl == 1 and sda_in != prev_sda:
        i2c_state = "IDLE"

    elif i2c_state == "IDLE":
        # I2C start condition
        if sda_in == 0:
            i2c_state = "START"
            i2c_index = 3

    elif i2c_state == "START":
        if sda_in == 0 and scl == 0 and prev_scl == 1:
            i2c_state = "R_ADDR"
            i2c_addr = LogicArray(0, Range(6, "downto", 0))
            i2c_counter = 6

    elif prev_scl == 0 and scl == 1:
        if i2c_state == "R_ADDR":
            # Posedge of scl
            i2c_addr[i2c_counter] = sda_in

        elif i2c_state == "R_CMD":
            i2c_cmd = sda_in

        elif i2c_state == "WRITE":
            i2c_current_recv[i2c_counter] = sda_in

    elif prev_scl == 1 and scl == 0:
        if i2c_state == "R_ADDR":
            if i2c_counter > 0:
                i2c_counter -= 1
            else:
                i2c_state = "R_CMD"

        elif i2c_state == "R_CMD":
            i2c_counter = 0
            i2c_state = "T_ACK"

        elif i2c_state == "T_ACK":
            i2c_counter = 7
            i2c_index = 3
            if i2c_cmd == 1:
                i2c_state = "READ"
            else:
                i2c_state = "WRITE"

        elif i2c_state == "WRITE":
            if i2c_counter > 0:
                i2c_counter -= 1
            else:
                i2c_recv.append(i2c_current_recv.to_unsigned())
                i2c_index -= 1
                i2c_counter = 7
                i2c_state = "WRITE_ACK"

        elif i2c_state == "WRITE_ACK":
            i2c_state = "WRITE"

        elif i2c_state == "READ":
            if i2c_counter > 0:
                i2c_counter -= 1
            else:
                i2c_index -= 1

                if i2c_index < 0:
                    i2c_index = 0

                i2c_counter = 7
                i2c_state = "READ_ACK"

        elif i2c_state == "READ_ACK":
            i2c_state = "READ"

    prev_scl = scl
    prev_sda = sda_in

    if i2c_state in ["T_ACK", "WRITE_ACK"]:
        dut.sda_i.set(Immediate(Logic(0)))
    elif i2c_state == "READ":
        dut.sda_i.set(Immediate(i2c_send[3-i2c_index][i2c_counter]))


@cocotb.test()
async def test_cpu_fibonacci_fast(dut):
    global mem_pattern
    mem_pattern = []
    mem_pattern_correct = [
        (160, 2), (161, 0), (162, 0), (163, 0),
        (164, 3), (165, 0), (166, 0), (167, 0),
        (168, 5), (169, 0), (170, 0), (171, 0),
        (172, 8), (173, 0), (174, 0), (175, 0),
        (176, 13), (177, 0), (178, 0), (179, 0),
        (180, 21), (181, 0), (182, 0), (183, 0),
        (184, 34), (185, 0), (186, 0), (187, 0),
        (188, 55), (189, 0), (190, 0), (191, 0),
        (192, 89), (193, 0), (194, 0), (195, 0),
    ]

    # Create a logger for this testbench
    logger = logging.getLogger("my_testbench")

    logger.info("Startup sequence...")

    # Start up
    await start_up(dut, "../fib.txt")
    logger.info("Testing basic fibonacci program")

    # Wait for a number of clock cycles
    for i in range(18000):
        await ClockCycles(dut.clk, 1)

        await do_spi(dut)

    # Check the end result of the counter
    print(mem_pattern)
    assert mem_pattern == mem_pattern_correct
    logger.info("Done!")


@cocotb.test()
async def test_cpu_analog_enables(dut):
    # Create a logger for this testbench
    logger = logging.getLogger("my_testbench")

    logger.info("Startup sequence...")

    # Start up
    await start_up(dut, "../analog_enables.txt")
    logger.info("Testing analog enable pins")

    dut.lo_Qx_i.set(Immediate(Logic(1)))
    dut.lo_Q_i.set(Immediate(Logic(0)))
    dut.ds_Q_n_i.set(Immediate(Logic(1)))
    dut.ds_Q_p_i.set(Immediate(Logic(0)))
    dut.lo_Ix_i.set(Immediate(Logic(1)))
    dut.lo_I_i.set(Immediate(Logic(0)))
    dut.ds_I_n_i.set(Immediate(Logic(1)))
    dut.ds_I_p_i.set(Immediate(Logic(0)))

    # Wait for a number of clock cycles
    for i in range(100000):
        await ClockCycles(dut.clk, 1)
        await do_spi(dut)

        # HACK: This code writes some input to the bidir pads in the first part of the test
        # The CPU will not drive those after reset, so that the analog part may be
        # used even if the CPU is not working properly.
        # In this test, the CPU will start driving the pads at some point, therefore
        # we set them to Z again. Otherwise, they would be X.
        # This allows us to verify that the internal routing works and inputs are correctly
        # rerouted to the outputs.
        if i < 10000:
            dut.lo_Qx_i.set(Immediate(not dut.lo_Qx_i.get()))
            dut.lo_Q_i.set(Immediate(not dut.lo_Q_i.get()))
            dut.ds_Q_n_i.set(Immediate(not dut.ds_Q_n_i.get()))
            dut.ds_Q_p_i.set(Immediate(not dut.ds_Q_p_i.get()))
            dut.lo_Ix_i.set(Immediate(not dut.lo_Ix_i.get()))
            dut.lo_I_i.set(Immediate(not dut.lo_I_i.get()))
            dut.ds_I_n_i.set(Immediate(not dut.ds_I_n_i.get()))
            dut.ds_I_p_i.set(Immediate(not dut.ds_I_p_i.get()))
        else:
            dut.lo_Qx_i.set(Immediate(Logic("Z")))
            dut.lo_Q_i.set(Immediate(Logic("Z")))
            dut.ds_Q_n_i.set(Immediate(Logic("Z")))
            dut.ds_Q_p_i.set(Immediate(Logic("Z")))
            dut.lo_Ix_i.set(Immediate(Logic("Z")))
            dut.lo_I_i.set(Immediate(Logic("Z")))
            dut.ds_I_n_i.set(Immediate(Logic("Z")))
            dut.ds_I_p_i.set(Immediate(Logic("Z")))

    logger.info("Done!")


@cocotb.test()
async def test_cpu_uart_tx(dut):
    global uart_rx_bytes

    uart_rx_bytes = list()  # List of bytes sent by the CPU to the tb

    # Create a logger for this testbench
    logger = logging.getLogger("my_testbench")

    logger.info("Startup sequence...")

    # Start up
    await start_up(dut, "../uart_tx_test.txt")
    logger.info("Testing UART transmission")

    # Wait for a number of clock cycles
    # for i in range(150000):
    for i in range(100000):
        await ClockCycles(dut.clk, 1)

        await do_spi(dut)
        await do_uart_rx(dut)

    # Check the end result of the counter
    print(uart_rx_bytes)
    assert uart_rx_bytes == ["H", "a", "l", "l", "o", "!"]
    # assert mem_pattern == mem_pattern_correct

    logger.info("Done!")


@cocotb.test()
async def test_cpu_uart_rx(dut):
    global uart_tx_enable
    global uart_tx_current_data
    global uart_rx_bytes

    uart_rx_bytes = list()  # List of bytes sent by the CPU to the tb
    # Create a logger for this testbench
    logger = logging.getLogger("my_testbench")

    logger.info("Startup sequence...")

    # Start up
    await start_up(dut, "../uart_rx_test.txt")
    logger.info("Testing UART receiving")

    to_send = ["L", "i", "n", "z"]
    counter = -1  # HACK
    next_i = 6000
    increment = 40000

    # Wait for a number of clock cycles
    for i in range(200000):
        await ClockCycles(dut.clk, 1)

        if i >= next_i:
            if uart_tx_enable == 0 and counter < len(to_send) - 1:
                counter += 1
                uart_tx_enable = 1
                uart_tx_current_data = LogicArray(ord(to_send[counter]), Range(7, "downto", 0))
                next_i = i + increment

        await do_spi(dut)
        await do_uart_rx(dut)
        await do_uart_tx(dut)

    # Check the end result of the counter
    print(uart_rx_bytes)
    assert uart_rx_bytes == to_send
    logger.info("Done!")


@cocotb.test()
async def test_cpu_i2c_rw(dut):
    global uart_tx_enable
    global uart_tx_current_data
    global uart_rx_bytes
    global i2c_recv

    i2c_recv = []
    uart_rx_bytes = list()  # List of bytes sent by the CPU to the tb
    # Create a logger for this testbench
    logger = logging.getLogger("my_testbench")

    logger.info("Startup sequence...")

    # Start up
    await start_up(dut, "../i2c_rw_test.txt")
    logger.info("Testing I2C")

    # Wait for a number of clock cycles
    for i in range(250000):
        await ClockCycles(dut.clk, 1)

        await do_spi(dut)
        await do_uart_rx(dut)
        await do_uart_tx(dut)
        await do_i2c_slave(dut)

    # Check the end result of the counter
    print(i2c_recv)
    assert i2c_recv == [0x78, 37, 37, 37, 29, 37, 29, 37, 29, 204, 103]
    logger.info("Done!")

@cocotb.test()
async def test_cpu_i2c_mc(dut):
    global uart_tx_enable
    global uart_tx_current_data
    global uart_rx_bytes
    global i2c_recv

    i2c_recv = []
    uart_rx_bytes = list()  # List of bytes sent by the CPU to the tb
    # Create a logger for this testbench
    logger = logging.getLogger("my_testbench")

    logger.info("Startup sequence...")

    # Start up
    await start_up(dut, "../i2c_mc_test.txt")
    logger.info("Testing I2C Multicycle")

    # Wait for a number of clock cycles
    for i in range(100000):
        await ClockCycles(dut.clk, 1)

        await do_spi(dut)
        await do_uart_rx(dut)
        await do_uart_tx(dut)
        await do_i2c_slave(dut)

    # Check the end result of the counter
    print(i2c_recv)
    assert i2c_recv == [32]
    logger.info("Done!")


@cocotb.test()
async def test_cpu_gpio(dut):
    # Create a logger for this testbench
    logger = logging.getLogger("my_testbench")

    logger.info("Startup sequence...")

    # Start up
    await start_up(dut, "../gpio_test.txt")
    logger.info("Testing GPIO")

    # Test 0111 + 1 = 1000
    dut.gpio_in.set(Immediate(0b0111))
    # Wait for a number of clock cycles

    print(dut.gpio_out.get())
    assert dut.gpio_out.get() == 0b0000
    for i in range(5000):
        await ClockCycles(dut.clk, 1)
        await do_spi(dut)

    # Check the end result of the counter
    print(dut.gpio_out.get())
    assert dut.gpio_out.get() == 0b1000

    # Test 1010 + 1 = 1011
    dut.gpio_in.set(Immediate(0b1010))
    # Wait for a number of clock cycles

    for i in range(5000):
        await ClockCycles(dut.clk, 1)
        await do_spi(dut)

    # Check the end result of the counter
    print(dut.gpio_out.get())
    assert dut.gpio_out.get() == 0b1011
    logger.info("Done!")


@cocotb.test()
async def test_cpu_wspr(dut):
    # Create a logger for this testbench
    logger = logging.getLogger("my_testbench")

    logger.info("Startup sequence...")

    # Start up
    await start_up(dut, "../wspr_test.txt")
    logger.info("Testing WSPR")

    for i in range(300000):
        await ClockCycles(dut.clk, 1)
        await do_spi(dut)

        if i == 19000:
            dut.gpio_in.set(Immediate(0b0001))

    print("WSPR TEST DONE. CHECK WAVEFORM!")
    logger.info("Done!")


def counter_top_runner():

    proj_path = Path(__file__).resolve().parent

    sources = []
    # defines = {f"SLOT_{slot.upper()}": True}
    defines = {}
    includes = [proj_path / "../src/"]

    if gl:
        # SCL models
        sources.append(Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / f"{scl}.v")
        sources.append(Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / f"sg13g2_udp.v")
        # sources.append(Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / "sg13g2_stdcell.v")

        # We use the unpowered netlist
        # sources.append(proj_path / f"../final/nl/{hdl_toplevel}.nl.v")
        sources.append(proj_path / f"../../../final/nl/counter_top.nl.v")

        defines = {"USE_POWER_PINS": False}
    else:
        sources.append(proj_path / "../../../rtl/constants.sv")
        sources.append(proj_path / "../../../rtl/counter_top.sv")
        sources.append(proj_path / "../../../rtl/alu.sv")
        sources.append(proj_path / "../../../rtl/lo_gen.v")
        sources.append(proj_path / "../../../rtl/csr.sv")
        sources.append(proj_path / "../../../rtl/memory.sv")
        sources.append(proj_path / "../../../rtl/dsmod.v")
        sources.append(proj_path / "../../../rtl/regs.sv")
        sources.append(proj_path / "../../../rtl/freq_generator.sv")
        sources.append(proj_path / "../../../rtl/spi_master.sv")
        sources.append(proj_path / "../../../rtl/control.sv")
        sources.append(proj_path / "../../../rtl/i2c_master.sv")
        sources.append(proj_path / "../../../rtl/i2c_master_mc.sv")
        sources.append(proj_path / "../../../rtl/cordic_iterative.v")
        sources.append(proj_path / "../../../rtl/imm_gen.sv")
        sources.append(proj_path / "../../../rtl/uart_tx.v")
        sources.append(proj_path / "../../../rtl/uart_rx.v")
        sources.append(proj_path / "../../../rtl/cordic_slice.v")
        sources.append(proj_path / "../../../rtl/instructioncounter.sv")

    build_args = []

    if sim == "icarus":
        # For debugging
        # build_args = ["-Winfloop", "-pfileline=1"]
        build_args = ["-DSIM"]
        pass

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
