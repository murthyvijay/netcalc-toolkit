"""ECMP flow hashing vs packet spraying: collisions and load imbalance.

AI training traffic is a few very large, long-lived flows ("elephants").
Classic ECMP hashes each flow onto one path, so with F flows over P equal
paths some paths get two or more flows while others idle. Packet spraying
(as in Ultra Ethernet and multipath RDMA transports) spreads each flow's
packets over all paths, making the load almost perfectly even.

This module gives closed-form collision probabilities and seeded Monte Carlo
estimates of the worst-path load, so results are reproducible.

Usage::

    python -m netcalc.aifabric.loadbalance collide --flows 8 --paths 16
    python -m netcalc.aifabric.loadbalance imbalance --flows 64 --paths 64
    python -m netcalc.aifabric.loadbalance imbalance --flows 64 --paths 64 --spray 256
"""

import argparse
import math
import random


def collision_probability(flows, paths):
    """Probability that at least two of ``flows`` hash onto the same path.

    The birthday problem: ``1 - P! / ((P - F)! * P^F)``.
    """
    if flows > paths:
        return 1.0
    log_no_collision = (math.lgamma(paths + 1) - math.lgamma(paths - flows + 1)
                        - flows * math.log(paths))
    return 1 - math.exp(log_no_collision)


def expected_idle_paths(flows, paths):
    """Expected number of paths that receive no flow: ``P (1 - 1/P)^F``."""
    return paths * (1 - 1 / paths) ** flows
