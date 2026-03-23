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


def bdp_bytes(rate_bps, rtt_s):
    """Bandwidth-delay product in bytes.

    >>> bdp_bytes(10e9, 0.08)
    100000000.0
    """
    return rate_bps * rtt_s / 8


def window_limited_throughput(window_bytes, rtt_s):
    """Maximum throughput (bps) of a single flow limited by its window."""
    return window_bytes * 8 / rtt_s


def window_scale_shift(window_bytes):
    """TCP window-scale shift count (RFC 7323) needed to advertise ``window_bytes``."""
    shift = 0
    while (65535 << shift) < window_bytes:
        shift += 1
    if shift > 14:
        raise ValueError("window exceeds the RFC 7323 maximum (shift 14, ~1 GiB)")
    return shift


def transfer_time(size_bytes, rate_bps, rtt_s=0.0, setup_rtts=1.0, efficiency=1.0):
    """Approximate wall-clock time to move ``size_bytes``.

    ``setup_rtts`` round trips for the handshake (1 for TCP, 2 with TLS 1.3
    over TCP), then the payload at ``rate_bps * efficiency`` plus half an
    RTT for the last byte to arrive.
    """
    return setup_rtts * rtt_s + size_bytes * 8 / (rate_bps * efficiency) + rtt_s / 2


def flows_to_fill(rate_bps, rtt_s, window_bytes):
    """Parallel window-limited flows needed to fill a link."""
    return math.ceil(rate_bps / window_limited_throughput(window_bytes, rtt_s))
