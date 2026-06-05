"""Switch buffer sizing: incast absorption and shared-buffer dynamic thresholds.

**Incast.** When N senders burst to one receiver port at line rate, the
port drains at 1x while (N)x arrives. A burst of B bytes per sender fills
``N * B - (drain during the burst)`` of buffer.

**Dynamic threshold (DT).** Shared-buffer switches cap each queue at
``alpha * free_buffer``. With n equally congested queues the steady-state
per-queue limit is ``alpha * B / (1 + alpha * n)``, leaving
``B / (1 + alpha * n)`` free for new bursts.

Usage::

    python -m netcalc.aifabric.buffer incast --senders 16 --burst 256KB --rate 400G
    python -m netcalc.aifabric.buffer dt --buffer 64MB --alpha 1 --queues 8
    python -m netcalc.aifabric.buffer absorb --buffer 16MB --senders 4 --rate 400G
"""

import argparse

from netcalc.units import fmt_size, fmt_time, parse_rate, parse_size


def incast_buffer(senders, burst_bytes, sender_rate_bps, port_rate_bps=None):
    """Peak queue (bytes) when ``senders`` each send ``burst_bytes`` at once.

    All senders transmit for ``burst / sender_rate`` seconds while the egress
    port drains at ``port_rate``; the queue peaks at the end of the burst.
    """
    port_rate = port_rate_bps or sender_rate_bps
    duration = burst_bytes * 8 / sender_rate_bps
    drained = port_rate * duration / 8
    return max(0.0, senders * burst_bytes - drained)
