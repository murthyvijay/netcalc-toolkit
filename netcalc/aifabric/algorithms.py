"""Collective algorithms compared: ring, tree, recursive halving-doubling and hierarchical all-reduce.

The alpha-beta model charges ``alpha`` per message (latency) and ``S / B``
per byte stream. For an all-reduce of S bytes over n ranks:

* **Ring**: ``2 (n - 1) alpha + 2 (n - 1) / n * S / B``. Bandwidth optimal,
  but latency grows linearly with n.
* **Double binary tree** (pipelined): ``2 log2(n) alpha + 2 S / B``
  approximately. Latency grows only with log n.
* **Recursive halving-doubling** (Rabenseifner): ``2 log2(n) alpha +
  2 (n - 1) / n * S / B``, for power-of-two n.
* **Hierarchical**: reduce-scatter inside each server over the fast
  scale-up link, all-reduce the 1/g shards across servers, all-gather
  inside again.

In this first-order model the tree's bandwidth term is only slightly worse
than the ring's, so trees win up to very large messages. Real pipelined trees
reach less than full link bandwidth; the ``efficiency`` factor models that and
pulls the ring/tree crossover down to practical sizes.

Usage::

    python -m netcalc.aifabric.algorithms compare --size 64MB --ranks 512 --bw 400G --alpha 5us
    python -m netcalc.aifabric.algorithms crossover --ranks 512 --bw 400G --alpha 5us
    python -m netcalc.aifabric.algorithms hierarchical --size 1GB --servers 64 --gpus 8 --bw 400G --intra-bw 3.6T
"""

import argparse
import math

from netcalc.units import fmt_size, fmt_time, parse_rate, parse_size, parse_time
