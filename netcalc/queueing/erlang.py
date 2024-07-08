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
