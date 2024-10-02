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
