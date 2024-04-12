"""Coherent line rates: baud, modulation, polarisation, FEC and spectral efficiency.

A coherent transceiver sends symbols on two polarisations::

    line rate = baud * bits_per_symbol * polarizations
    net rate  = line rate / ((1 + FEC overhead) * (1 + framing overhead))
    occupied  = baud * (1 + roll-off)                 (Nyquist-shaped spectrum)
    SE        = net rate / channel spacing            (b/s/Hz)

For example 400ZR runs DP-16QAM at 59.84 GBd: ``59.84 * 4 * 2 = 478.75``
Gb/s on the line, which carries 400GbE after concatenated FEC (about
14.8 %) and framing. Probabilistic constellation shaping (PCS) gives a
fractional number of bits per symbol, so this module accepts a float too.

Usage::

    python -m netcalc.optics.coherent rate --baud 59.84 --mod 16qam --fec 0.148
    python -m netcalc.optics.coherent baud --net 800 --mod 16qam --fec 0.15
    python -m netcalc.optics.coherent capacity --net 400 --spacing 75
"""

import argparse
import math

MODULATION_BITS = {"bpsk": 1, "qpsk": 2, "8qam": 3, "16qam": 4, "32qam": 5, "64qam": 6}
C_BAND_GHZ = 4800.0


def bits_per_symbol(modulation):
    """Bits per symbol per polarisation for a name (``"16qam"``) or a number.

    >>> bits_per_symbol("16QAM"), bits_per_symbol(3.5)
    (4, 3.5)
    """
    if isinstance(modulation, str):
        key = modulation.lower().replace("dp-", "").replace("-", "")
        if key in MODULATION_BITS:
            return MODULATION_BITS[key]
        return float(key)
    return modulation


def line_rate_gbps(baud_g, modulation, polarizations=2):
    """Raw line rate (Gb/s) before FEC and framing are removed."""
    return baud_g * bits_per_symbol(modulation) * polarizations
