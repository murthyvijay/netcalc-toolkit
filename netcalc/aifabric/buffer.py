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


def absorb_time(buffer_bytes, senders, sender_rate_bps, port_rate_bps=None):
    """How long a buffer absorbs ``senders`` at full rate before overflowing."""
    port_rate = port_rate_bps or sender_rate_bps
    excess = senders * sender_rate_bps - port_rate
    if excess <= 0:
        return float("inf")
    return buffer_bytes * 8 / excess


def dt_queue_limit(buffer_bytes, alpha, congested_queues):
    """Steady-state per-queue limit under the dynamic threshold algorithm."""
    return alpha * buffer_bytes / (1 + alpha * congested_queues)


def dt_free_buffer(buffer_bytes, alpha, congested_queues):
    """Buffer left free when ``congested_queues`` sit at their DT limit."""
    return buffer_bytes / (1 + alpha * congested_queues)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("incast")
    p.add_argument("--senders", type=int, required=True)
    p.add_argument("--burst", required=True)
    p.add_argument("--rate", required=True, help="sender and port rate")
    p = sub.add_parser("dt")
    p.add_argument("--buffer", required=True)
    p.add_argument("--alpha", type=float, default=1.0)
    p.add_argument("--queues", type=int, required=True)
    p = sub.add_parser("absorb")
    p.add_argument("--buffer", required=True)
    p.add_argument("--senders", type=int, required=True)
    p.add_argument("--rate", required=True)
    args = parser.parse_args(argv)

    if args.cmd == "incast":
        b = incast_buffer(args.senders, parse_size(args.burst), parse_rate(args.rate))
        print(f"peak queue = {fmt_size(b)}")
    elif args.cmd == "dt":
        buf = parse_size(args.buffer)
        print(f"per-queue limit = {fmt_size(dt_queue_limit(buf, args.alpha, args.queues))}, "
              f"free = {fmt_size(dt_free_buffer(buf, args.alpha, args.queues))}")
    else:
        t = absorb_time(parse_size(args.buffer), args.senders, parse_rate(args.rate))
        print(f"buffer absorbs the incast for {fmt_time(t)}")


if __name__ == "__main__":
    main()
