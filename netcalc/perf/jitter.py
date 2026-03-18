"""Jitter: RFC 3550 interarrival jitter, IPDV and delay statistics.

RTP (RFC 3550, section 6.4.1) defines interarrival jitter as a running
estimate of the mean deviation of the transit-time difference between
consecutive packets::

    D(i-1, i) = (R_i - R_(i-1)) - (S_i - S_(i-1))
    J = J + (|D(i-1, i)| - J) / 16

where S is the sender timestamp and R the receive time. Clock offset
between the hosts cancels out, so the two clocks need not be synchronised.

IP packet delay variation (IPDV, RFC 3393/5481) is the sequence of
consecutive one-way delay differences; PDV is each delay minus the minimum.

Usage::

    python -m netcalc.perf.jitter rfc3550 --send 0 20 40 60 --recv 5 26 44 67
    python -m netcalc.perf.jitter stats 10.1 10.4 9.8 12.0 10.2
    python -m netcalc.perf.jitter file delays.csv      # columns: send,recv
"""

import argparse
import csv
import math
import statistics


def rfc3550_series(send_times, recv_times):
    """Jitter estimate after every packet, starting from J = 0."""
    if len(send_times) != len(recv_times) or len(send_times) < 2:
        raise ValueError("need two equal-length lists with at least two packets")
    j, series = 0.0, []
    for i in range(1, len(send_times)):
        d = (recv_times[i] - recv_times[i - 1]) - (send_times[i] - send_times[i - 1])
        j += (abs(d) - j) / 16
        series.append(j)
    return series


def rfc3550_jitter(send_times, recv_times):
    """Final RFC 3550 jitter estimate (same units as the inputs)."""
    return rfc3550_series(send_times, recv_times)[-1]
