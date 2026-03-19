"""Packet loss: loss ratio, multi-hop loss, burst analysis from sequence numbers.

Average loss hides the behaviour that hurts applications: bursts. This
module reports both, and composes per-hop loss into end-to-end loss.

Usage::

    python -m netcalc.perf.loss ratio --sent 100000 --received 99950
    python -m netcalc.perf.loss path 0.001 0.0005 0.002
    python -m netcalc.perf.loss seq 1 2 3 6 7 7 5 8 12
    python -m netcalc.perf.loss any --loss 1e-4 --packets 5000
"""

import argparse


def loss_ratio(sent, received):
    """Fraction of packets lost: ``(sent - received) / sent``."""
    if sent <= 0:
        raise ValueError("sent must be positive")
    return (sent - received) / sent


def path_loss(*hop_loss):
    """End-to-end loss across independent hops: ``1 - prod(1 - p_i)``."""
    survive = 1.0
    for p in hop_loss:
        survive *= 1 - p
    return 1 - survive
