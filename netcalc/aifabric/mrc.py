"""Multipath reliable connection (MRC) sizing.

A multipath reliable connection keeps one reliable transport session but
sends its packets over many network paths, usually by varying an entropy
value (for example the UDP source port) that switches hash on. The design
questions are arithmetic:

* How many entropy values do I need so that every path is used?
  (coupon collector: about ``P * H(P)`` random values for P paths)
* What capacity remains when some paths fail?
* How big must the receiver's reorder buffer be, given the delay skew
  between the fastest and slowest path?

Usage::

    python -m netcalc.aifabric.mrc entropy --paths 64
    python -m netcalc.aifabric.mrc coverage --paths 64 --values 256
    python -m netcalc.aifabric.mrc failover --paths 8 --path-rate 400G --failed 1
    python -m netcalc.aifabric.mrc reorder --rate 800G --skew 4us --mtu 4096
"""

import argparse
import math

from netcalc.units import fmt_rate, fmt_size, parse_rate, parse_size, parse_time


def harmonic(n):
    """n-th harmonic number H(n) = 1 + 1/2 + ... + 1/n."""
    return sum(1 / i for i in range(1, n + 1))


def expected_entropies_to_cover(paths):
    """Expected random entropy values until every path has been hit: P * H(P)."""
    return paths * harmonic(paths)


def coverage_probability(paths, values):
    """Probability that ``values`` random entropies hit all ``paths``.

    Inclusion-exclusion: ``sum_k (-1)^k C(P, k) (1 - k/P)^V``.
    """
    total = sum((-1) ** k * math.comb(paths, k) * (1 - k / paths) ** values
                for k in range(paths + 1))
    return min(1.0, max(0.0, total))


def expected_paths_used(paths, values):
    """Expected number of distinct paths hit by ``values`` entropies."""
    return paths * (1 - (1 - 1 / paths) ** values)


def failover_capacity(paths, path_rate_bps, failed=0):
    """Aggregate capacity with ``failed`` paths removed from the spray set."""
    if failed > paths:
        raise ValueError("more failed paths than paths")
    return (paths - failed) * path_rate_bps
