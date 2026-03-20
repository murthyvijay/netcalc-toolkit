"""Throughput, bandwidth-delay product (BDP) and transfer time.

A sender can have at most one window of data in flight per round trip, so::

    throughput <= window / RTT
    BDP = rate * RTT          (bytes needed in flight to fill the pipe)

Usage::

    python -m netcalc.perf.throughput bdp --rate 10G --rtt 80ms
    python -m netcalc.perf.throughput window --window 64KB --rtt 30ms
    python -m netcalc.perf.throughput transfer --size 10GB --rate 1G --rtt 50ms
"""

import argparse
import math

from netcalc.units import fmt_rate, fmt_size, fmt_time, parse_rate, parse_size, parse_time
