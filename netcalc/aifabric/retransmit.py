"""Loss recovery: go-back-N vs selective retransmission, tail-latency cost.

RoCEv2 NICs traditionally recover from loss with go-back-N: after a gap
the receiver NAKs and the sender resends everything from the lost packet,
which is why RoCE fabrics are built lossless with PFC. Ultra Ethernet's
transport and other multipath RDMA designs use selective retransmission,
so a lost packet costs about one packet, and spraying-induced reordering is
tolerated.

Models used (``p`` = packet loss ratio, ``W`` = packets in flight):

* selective repeat efficiency ``= 1 - p``
* go-back-N efficiency ``= (1 - p) / (1 - p + p * W)``
* chance a message of N packets needs any retransmission ``= 1 - (1 - p)^N``

Usage::

    python -m netcalc.aifabric.retransmit compare --loss 1e-4 --rate 400G --rtt 10us --mtu 4096
    python -m netcalc.aifabric.retransmit message --loss 1e-5 --size 64MB --mtu 4096 --rto 1ms
"""

import argparse
import math

from netcalc.perf.throughput import bdp_bytes
from netcalc.units import fmt_rate, fmt_time, parse_rate, parse_size, parse_time


def window_packets(rate_bps, rtt_s, mtu_bytes):
    """Packets in flight needed to fill the pipe (BDP / MTU, at least 1)."""
    return max(1, math.ceil(bdp_bytes(rate_bps, rtt_s) / mtu_bytes))


def selective_efficiency(loss):
    """Goodput fraction with selective retransmission."""
    return 1 - loss


def go_back_n_efficiency(loss, window):
    """Goodput fraction with go-back-N and ``window`` packets in flight."""
    return (1 - loss) / (1 - loss + loss * window)


def message_retransmit_probability(loss, packets):
    """Probability that a message of ``packets`` sees at least one loss."""
    return 1 - (1 - loss) ** packets


def expected_message_time(size_bytes, rate_bps, mtu_bytes, loss, recovery_s):
    """Expected completion time of one message including loss recovery.

    Adds ``recovery_s`` (an RTO or a NAK round trip) weighted by the chance
    the message needs any retransmission. Collective operations wait for the
    slowest message, so this tail matters more than the average.
    """
    packets = math.ceil(size_bytes / mtu_bytes)
    base = size_bytes * 8 / rate_bps
    return base + message_retransmit_probability(loss, packets) * recovery_s
