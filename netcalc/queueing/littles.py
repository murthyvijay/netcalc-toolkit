"""Little's law and the operational laws of queueing.

Little's law holds for any stable system, whatever the arrival or service
distributions::

    L = lambda * W

(mean number in the system = arrival rate x mean time in the system). Two
companions from operational analysis:

* **Utilisation law**: ``U = X * S`` (throughput x service time per job).
* **Buffer occupancy**: bytes sitting in a queue = drain rate x queueing
  delay, so 10 us of queueing on a 400 Gb/s port is 500 KB of buffer.

Usage::

    python -m netcalc.queueing.littles solve --rate 2000 --time 0.05
    python -m netcalc.queueing.littles solve --count 40 --rate 2000
    python -m netcalc.queueing.littles buffer --rate 400G --delay 10us
"""

import argparse

from netcalc.units import fmt_size, fmt_time, parse_rate, parse_time


def littles_law(count=None, rate=None, time=None):
    """Solve ``L = lambda * W`` for whichever of the three is ``None``.

    >>> littles_law(rate=2000, time=0.05)
    100.0
    >>> littles_law(count=40, rate=2000)
    0.02
    """
    missing = [name for name, v in (("count", count), ("rate", rate), ("time", time)) if v is None]
    if len(missing) != 1:
        raise ValueError("give exactly two of count, rate and time")
    if count is None:
        return float(rate * time)
    if rate is None:
        return count / time
    return count / rate
