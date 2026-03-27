"""TCP throughput models: Mathis and Padhye (PFTK).

The Mathis et al. (1997) model gives the steady-state throughput of a
Reno-style TCP flow that sees random loss ``p``::

    throughput = (MSS / RTT) * (C / sqrt(p)),   C = sqrt(3/2) ~ 1.22

Padhye et al. (1998) extend it with retransmission timeouts, which dominate
at higher loss::

    B = MSS / (RTT*sqrt(2bp/3) + RTO*min(1, 3*sqrt(3bp/8)) * p * (1 + 32p^2))

where ``b`` is packets acknowledged per ACK (2 with delayed ACKs).

Both describe loss-based congestion control (Reno/CUBIC-like behaviour at
moderate BDP); BBR and datacenter transports behave differently.

Usage::

    python -m netcalc.perf.tcp mathis --mss 1460 --rtt 50ms --loss 1e-4
    python -m netcalc.perf.tcp padhye --mss 1460 --rtt 50ms --loss 1e-2 --rto 200ms
    python -m netcalc.perf.tcp max-loss --mss 1460 --rtt 50ms --rate 1G
"""

import argparse
import math

from netcalc.units import fmt_rate, parse_rate, parse_time

MATHIS_C = math.sqrt(3 / 2)


def mathis_throughput(mss_bytes, rtt_s, loss, c=MATHIS_C):
    """Mathis model throughput in bits per second."""
    if loss <= 0:
        raise ValueError("loss must be > 0 for the Mathis model")
    return mss_bytes * 8 / rtt_s * c / math.sqrt(loss)


def mathis_max_loss(mss_bytes, rtt_s, rate_bps, c=MATHIS_C):
    """Highest loss rate at which one flow can still reach ``rate_bps``."""
    return (mss_bytes * 8 * c / (rtt_s * rate_bps)) ** 2
