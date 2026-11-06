# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Test the substrate tie of a kpex 2.5D netlist, run by `make regression`.

import os
import tempfile
import unittest

from tie_pex_substrate import tie


def run_tie(text, net="vss"):
    """The netlist after the tie of port sub! to `net`."""
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "cell.spice")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        tie(path, net, "sub!")
        with open(path, encoding="utf-8") as f:
            return f.read()


class TieTest(unittest.TestCase):
    def test_ports_on_one_line(self):
        text = (".SUBCKT top vdd vss sub! a\n"
                "X1 a b vss sub! nmos w=1\n"
                "C1 sub! vss 1f\n"
                "C2 sub! a 2f\n"
                ".ENDS top\n")
        self.assertEqual(run_tie(text), (".SUBCKT top vdd vss a\n"
                                         "X1 a b vss vss nmos w=1\n"
                                         "C2 vss a 2f\n"
                                         ".ENDS top\n"))

    def test_net_on_continuation_line(self):
        text = (".SUBCKT top a sub! b\n"
                "+ c vss\n"
                "C1 sub! a 1f\n"
                ".ENDS top\n")
        self.assertEqual(run_tie(text), (".SUBCKT top a b c vss\n"
                                         "C1 vss a 1f\n"
                                         ".ENDS top\n"))

    def test_substrate_on_continuation_line(self):
        text = (".SUBCKT top vss a\n"
                "+ sub! b\n"
                "C1 sub! a 1f\n"
                ".ENDS top\n")
        self.assertEqual(run_tie(text), (".SUBCKT top vss a b\n"
                                         "C1 vss a 1f\n"
                                         ".ENDS top\n"))

    def test_substrate_on_continuation_line_of_device(self):
        text = (".SUBCKT top vss sub! a\n"
                "X1 a b vss\n"
                "+ sub! nmos w=1\n"
                ".ENDS top\n")
        self.assertEqual(run_tie(text), (".SUBCKT top vss a\n"
                                         "X1 a b vss\n"
                                         "+ vss nmos w=1\n"
                                         ".ENDS top\n"))

    def test_no_substrate_port_keeps_file(self):
        text = (".SUBCKT top vss a\n"
                "+ b\n"
                "C1 vss a 1f\n"
                ".ENDS top\n")
        self.assertEqual(run_tie(text), text)

    def test_net_is_no_port(self):
        text = (".SUBCKT top a sub! b\n"
                "+ c\n"
                ".ENDS top\n")
        with self.assertRaises(SystemExit):
            run_tie(text)


if __name__ == "__main__":
    unittest.main()
