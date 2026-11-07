# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Check the spectrum code of sim_trannoise.py on period jitter with a known PSD, without a simulator.

import sys

import numpy as np

from sim_trannoise import phase_noise, reference_at, smooth

F0 = 20e9  # Hz, carrier of the synthetic records
F_RES = F0 / 4000.5  # Hz, Welch resolution: 4000 bins, whichever way the mean period rounds, an even count holds a Nyquist bin
SIGMA = 1e-3  # rad, per period, of the white phase differences
SEEDS = 8
PERIODS = 200000


def main():
    rng = np.random.default_rng(1)
    crossings = [np.cumsum((1 + SIGMA / (2 * np.pi) * rng.standard_normal(PERIODS)) / F0) for _ in range(SEEDS)]
    f0, f, per_seed, _ = phase_noise(crossings, F_RES)
    mean = 10 * np.log10(np.mean(10 ** (per_seed / 10), axis=0))
    fb, lb, nb = smooth(f, mean)
    expected = 10 * np.log10(SIGMA ** 2 / f0 / (4 * np.sin(np.pi * fb / f0) ** 2))
    low = fb < 1e9

    bin_width = f0 / int(f0 / F_RES)
    errors = []
    if abs(f[0] / bin_width - 2) > 1e-6:
        errors.append(f"the spectrum starts at bin {f[0] / bin_width:.3f}, bin 1 reads low and has to go")
    if abs(f[-1] / f0 - 0.5) < 0.1 * bin_width / f0:
        errors.append("the spectrum still holds the Nyquist bin")
    if nb.sum() != f.size:
        errors.append(f"the bands hold {nb.sum()} of {f.size} bins")
    if abs(fb[0] / f[0] - 1) > 1e-9:
        errors.append(f"the band of the lowest bin is labeled {fb[0] / f[0]:.4f} times that bin's frequency")
    if np.max(np.abs(lb[low] - expected[low])) > 1.5:
        errors.append(f"L is {np.max(np.abs(lb[low] - expected[low])):.2f} dB off the known PSD")
    if not np.array_equal(np.isnan(reference_at(np.array([1e6, 1e8, 2e8]), np.array([1e4, 1e8]), np.array([-60.0, -140.0]))), [False, False, True]):
        errors.append("the PNOISE reference is not NaN above its sweep")

    for error in errors:
        print(f"check_trannoise.py: {error}", file=sys.stderr)
    if errors:
        sys.exit(1)
    print(f"check_trannoise.py: pass, {fb.size} bands, L at most {np.max(np.abs(lb[low] - expected[low])):.2f} dB off the known PSD")


if __name__ == "__main__":
    main()
