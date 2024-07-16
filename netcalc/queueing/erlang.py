"""Erlang B and Erlang C: trunk, port and agent sizing.

Offered traffic in Erlangs is ``A = calls per hour * mean holding time (s) / 3600``.

* **Erlang B** (blocked calls cleared, M/M/c/c) gives the probability that
  a call finds all ``c`` circuits busy. It is computed with the stable
  recursion ``B(0) = 1``, ``B(n) = A B(n-1) / (n + A B(n-1))``. Used for
  SIP trunks, PRI channels, NAT port pools and any "reject when full"
  resource.
* **Erlang C** (blocked calls wait, M/M/c) gives the probability of waiting::

      C = c B / (c - A (1 - B))

  with mean wait ``C * AHT / (c - A)`` and service level
  ``P(wait <= t) = 1 - C exp(-(c - A) t / AHT)``.

Usage::

    python -m netcalc.queueing.erlang b --traffic 10 --servers 15
    python -m netcalc.queueing.erlang size --traffic 10 --blocking 0.01
    python -m netcalc.queueing.erlang c --traffic 10 --servers 12 --aht 180 --target 20
"""

import argparse
import math


def offered_traffic(calls_per_hour, holding_time_s):
    """Offered load in Erlangs.

    >>> offered_traffic(300, 120)
    10.0
    """
    return calls_per_hour * holding_time_s / 3600.0


def erlang_b(traffic, servers):
    """Blocking probability with ``servers`` circuits offered ``traffic`` Erlangs.

    >>> round(erlang_b(10, 15), 4)
    0.0365
    """
    b = 1.0
    for n in range(1, servers + 1):
        b = traffic * b / (n + traffic * b)
    return b


def servers_for_blocking(traffic, target):
    """Fewest circuits that keep Erlang B blocking at or below ``target``."""
    n = 0
    b = 1.0
    while b > target:
        n += 1
        b = traffic * b / (n + traffic * b)
    return n


def erlang_c(traffic, servers):
    """Probability that an arrival has to wait (``servers`` must exceed ``traffic``)."""
    if servers <= traffic:
        return 1.0
    b = erlang_b(traffic, servers)
    return servers * b / (servers - traffic * (1 - b))


def mean_wait(traffic, servers, holding_time_s):
    """Mean wait (s) over all arrivals in an M/M/c queue."""
    if servers <= traffic:
        return float("inf")
    return erlang_c(traffic, servers) * holding_time_s / (servers - traffic)


def service_level(traffic, servers, holding_time_s, target_s):
    """Fraction of arrivals answered within ``target_s`` seconds."""
    if servers <= traffic:
        return 0.0
    return 1 - erlang_c(traffic, servers) * math.exp(-(servers - traffic) * target_s / holding_time_s)
