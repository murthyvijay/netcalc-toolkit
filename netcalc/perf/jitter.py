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
