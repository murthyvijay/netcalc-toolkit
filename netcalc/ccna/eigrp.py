"""EIGRP classic composite metric and the feasibility condition.

With K values (K1..K5) the classic metric is::

    BW    = 10^7 / minimum bandwidth along the path (kbps)
    DELAY = sum of interface delays (microseconds) / 10
    metric = 256 * (K1*BW + K2*BW/(256 - load) + K3*DELAY)
    if K5 != 0: metric *= K5 / (reliability + K4)

Defaults are K1 = K3 = 1, K2 = K4 = K5 = 0, so the metric reduces to
``256 * (BW + DELAY)``. Integer division follows IOS behaviour.

Usage::

    python -m netcalc.ccna.eigrp metric --bw-kbps 100000 1000000 --delay-us 100 10
    python -m netcalc.ccna.eigrp fs --fd 28160 --rd 25600 30720
"""

import argparse

DEFAULT_K = (1, 0, 1, 0, 0)


def classic_metric(bandwidths_kbps, delays_us, k=DEFAULT_K, load=1, reliability=255):
    """EIGRP classic composite metric for a path."""
    k1, k2, k3, k4, k5 = k
    bw = 10 ** 7 // min(bandwidths_kbps)
    delay = sum(delays_us) // 10
    metric = k1 * bw + (k2 * bw) // (256 - load) + k3 * delay
    if k5:
        metric = metric * k5 // (reliability + k4)
    return 256 * metric


def is_feasible_successor(reported_distance, feasible_distance):
    """Feasibility condition: RD must be strictly less than the current FD."""
    return reported_distance < feasible_distance
