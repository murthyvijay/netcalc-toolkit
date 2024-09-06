"""RED / WRED: average queue tracking and early-drop (or ECN-mark) probability.

Random Early Detection works on an exponentially weighted moving average of
the queue depth, so short bursts pass but standing queues are trimmed::

    avg = (1 - w) * avg + w * q            w = 2^-n (Cisco's exponential weight, n = 9)

The drop probability rises linearly from 0 at ``min_th`` to ``1/MPD`` at
``max_th`` (MPD = mark probability denominator) and is 1 above ``max_th``.
Floyd and Jacobson spread drops evenly by scaling with the number of packets
since the last drop: ``pa = pb / (1 - count * pb)``. Weighted RED keeps one
profile per drop precedence, with lower thresholds for traffic that should
go first (for example AFx3 before AFx2 before AFx1).

Usage::

    python -m netcalc.traffic.wred prob --avg 35 --min 20 --max 40 --mpd 10
    python -m netcalc.traffic.wred ewma --n 9 0 50 50 50 50
    python -m netcalc.traffic.wred profiles --limit 64
"""

import argparse
import math


def drop_probability(avg, min_th, max_th, mpd=10):
    """Early-drop probability for an average queue depth.

    >>> drop_probability(30, 20, 40, mpd=10)
    0.05
    """
    if avg < min_th:
        return 0.0
    if avg >= max_th:
        return 1.0
    return (avg - min_th) / (max_th - min_th) / mpd
