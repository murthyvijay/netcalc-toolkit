"""Link schedulers: max-min fairness, weighted shares, DWRR quanta and priority blocking.

* **Max-min fair share** (water filling): no class gets more than it asks
  for, and spare capacity is split between the remaining classes in
  proportion to their weights. This is what WFQ and DWRR converge to under
  sustained load.
* **DWRR quanta** must be at least one MTU so every queue can send a packet
  per round; quanta proportional to the weights, scaled so the smallest is
  one MTU, keep rounds short and the shares exact.
* **Strict priority** serves its queue first, so lower classes only get the
  residual capacity, and even a priority packet can wait behind one
  non-preemptible maximum-size frame already on the wire.

Usage::

    python -m netcalc.traffic.scheduler fair --capacity 10G A=2G B=6G C=6G
    python -m netcalc.traffic.scheduler fair --capacity 10G A=8G:3 B=8G:1
    python -m netcalc.traffic.scheduler dwrr --mtu 9216 gold=5 silver=3 bronze=1
    python -m netcalc.traffic.scheduler blocking --frame 9216 --rate 10G
"""

import argparse

from netcalc.units import fmt_rate, fmt_time, parse_rate


def max_min_fair(capacity, demands, weights=None):
    """Weighted max-min fair allocation of ``capacity`` between ``{name: demand}``.

    >>> max_min_fair(10, {"A": 2, "B": 6, "C": 6})
    {'A': 2.0, 'B': 4.0, 'C': 4.0}
    """
    weights = weights or {name: 1.0 for name in demands}
    alloc = {name: 0.0 for name in demands}
    active = {name for name, d in demands.items() if d > 0}
    remaining = float(capacity)
    while active and remaining > 1e-12:
        total_w = sum(weights[n] for n in active)
        share = {n: remaining * weights[n] / total_w for n in active}
        satisfied = {n for n in active if demands[n] - alloc[n] <= share[n] + 1e-12}
        if not satisfied:
            for n in active:
                alloc[n] += share[n]
            break
        for n in satisfied:
            remaining -= demands[n] - alloc[n]
            alloc[n] = float(demands[n])
        active -= satisfied
    return alloc
