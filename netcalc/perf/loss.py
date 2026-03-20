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


def prob_any_loss(loss, packets):
    """Probability that at least one of ``packets`` is lost (e.g. a whole message)."""
    return 1 - (1 - loss) ** packets


def expected_transmissions(loss):
    """Mean transmissions per packet with retransmit-until-success: 1 / (1 - p)."""
    return 1 / (1 - loss)


def analyze_sequence(seqs):
    """Analyse received sequence numbers.

    Returns counts of unique packets, lost, duplicate and reordered packets,
    plus loss bursts (runs of consecutive missing numbers) between the first
    and the highest sequence number seen.
    """
    if not seqs:
        raise ValueError("no sequence numbers")
    seen, duplicates, reordered, highest = set(), 0, 0, None
    for s in seqs:
        if s in seen:
            duplicates += 1
            continue
        if highest is not None and s < highest:
            reordered += 1
        seen.add(s)
        highest = s if highest is None else max(highest, s)
    first = min(seen)
    missing = [s for s in range(first, highest + 1) if s not in seen]
    bursts, run = [], 0
    for s in range(first, highest + 2):
        if s <= highest and s not in seen:
            run += 1
        elif run:
            bursts.append(run)
            run = 0
    expected = highest - first + 1
    return {
        "expected": expected,
        "received": len(seen),
        "lost": len(missing),
        "loss_ratio": len(missing) / expected,
        "duplicates": duplicates,
        "reordered": reordered,
        "bursts": len(bursts),
        "max_burst": max(bursts, default=0),
        "mean_burst": sum(bursts) / len(bursts) if bursts else 0.0,
    }
