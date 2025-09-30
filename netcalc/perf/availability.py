"""Availability: series and parallel systems, nines, downtime and MTBF/MTTR.

* Steady-state availability of a component is ``A = MTBF / (MTBF + MTTR)``.
* Components in **series** (all must work) multiply: ``A = A1 * A2 * ...``.
* Redundant components in **parallel** (any one is enough) fail together
  only if all fail: ``A = 1 - (1 - A1)(1 - A2)...``.
* **k-of-n** redundancy (at least k of n identical parts up) follows the
  binomial distribution.
* "Nines": 99.99 % is four nines, about 52.6 minutes of downtime a year.

Usage::

    python -m netcalc.perf.availability series 0.999 0.9995 0.9999
    python -m netcalc.perf.availability parallel 0.99 0.99
    python -m netcalc.perf.availability mtbf --mtbf 50000h --mttr 4h
    python -m netcalc.perf.availability nines 0.9999
"""

import argparse
import math

HOURS_PER_YEAR = 8766.0


def from_mtbf(mtbf, mttr):
    """Availability from mean time between failures and mean time to repair."""
    return mtbf / (mtbf + mttr)


def series(*availabilities):
    """Availability of components that must all work.

    >>> round(series(0.999, 0.999), 6)
    0.998001
    """
    return math.prod(availabilities)
