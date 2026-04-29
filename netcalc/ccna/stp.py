"""Spanning Tree: timers, port costs, bridge IDs and root election.

IEEE 802.1D derives the timers from the network diameter (bridges across)
and the hello time::

    max_age       = 4 * hello + 2 * diameter - 2
    forward_delay = ceil((4 * hello + 3 * diameter) / 2)

With hello = 2 s and diameter = 7 this gives the familiar 20 s / 15 s, and
classic STP needs up to ``max_age + 2 * forward_delay`` = 50 s to converge
after an indirect failure. RSTP (802.1w) converges in about three hellos.

Usage::

    python -m netcalc.ccna.stp timers --diameter 7 --hello 2
    python -m netcalc.ccna.stp cost 10G
    python -m netcalc.ccna.stp root 32768:0011.2233.4455 4096:00aa.bbcc.ddee
"""

import argparse
import math

from netcalc.units import parse_rate

SHORT_COSTS = [(10e9, 2), (1e9, 4), (100e6, 19), (10e6, 100)]
