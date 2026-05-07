// SPDX-FileCopyrightText: 2025-2026 Simon Dorrer
// SPDX-License-Identifier: Apache-2.0
// Description: Shared constants for the counter macro.

`ifndef __COUNTER_CONSTANTS__
`define __COUNTER_CONSTANTS__

package counter_pkg;
  // Default upper bound (inclusive) of the counter range: counts 0 .. COUNTER_MAX
  parameter int COUNTER_MAX_DEFAULT = 15;

  // Bit width required to hold values 0 .. COUNTER_MAX (inclusive)
  parameter int COUNTER_BITWIDTH_DEFAULT = $clog2(COUNTER_MAX_DEFAULT + 1);
endpackage

`endif
