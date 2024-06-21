"""Little's law and the operational laws of queueing.

Little's law holds for any stable system, whatever the arrival or service
distributions::

    L = lambda * W

(mean number in the system = arrival rate x mean time in the system). Two
companions from operational analysis:

* **Utilisation law**: ``U = X * S`` (throughput x service time per job).
* **Buffer occupancy**: bytes sitting in a queue = drain rate x queueing
  delay, so 10 us of queueing on a 400 Gb/s port is 500 KB of buffer.

Usage::

    python -m netcalc.queueing.littles solve --rate 2000 --time 0.05
    python -m netcalc.queueing.littles solve --count 40 --rate 2000
    python -m netcalc.queueing.littles buffer --rate 400G --delay 10us
"""

import argparse

from netcalc.units import fmt_size, fmt_time, parse_rate, parse_time


def littles_law(count=None, rate=None, time=None):
    """Solve ``L = lambda * W`` for whichever of the three is ``None``.

    >>> littles_law(rate=2000, time=0.05)
    100.0
    >>> littles_law(count=40, rate=2000)
    0.02
    """
    missing = [name for name, v in (("count", count), ("rate", rate), ("time", time)) if v is None]
    if len(missing) != 1:
        raise ValueError("give exactly two of count, rate and time")
    if count is None:
        return float(rate * time)
    if rate is None:
        return count / time
    return count / rate


def utilization(throughput, service_time):
    """Utilisation law ``U = X * S``; values above 1 mean the server cannot keep up."""
    return throughput * service_time


def max_throughput(service_time, servers=1):
    """Saturation throughput (jobs/s) of ``servers`` identical servers."""
    return servers / service_time


def buffer_bytes(rate_bps, delay_s):
    """Bytes queued when a port draining at ``rate_bps`` shows ``delay_s`` of delay."""
    return rate_bps * delay_s / 8


def delay_from_buffer(rate_bps, queued_bytes):
    """Queueing delay (s) of ``queued_bytes`` ahead of a packet on a ``rate_bps`` port."""
    return queued_bytes * 8 / rate_bps


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("solve", help="solve L = lambda * W (give any two)")
    p.add_argument("--count", type=float, help="mean number in system (L)")
    p.add_argument("--rate", type=float, help="arrival rate per second (lambda)")
    p.add_argument("--time", type=float, help="mean time in system in seconds (W)")
    p = sub.add_parser("buffer", help="buffer occupancy from queueing delay")
    p.add_argument("--rate", required=True, help="port rate, e.g. 400G")
    p.add_argument("--delay", required=True, help="queueing delay, e.g. 10us")
    p = sub.add_parser("delay", help="queueing delay from buffer occupancy")
    p.add_argument("--rate", required=True)
    p.add_argument("--bytes", type=float, required=True)
    args = parser.parse_args(argv)

    if args.cmd == "solve":
        value = littles_law(args.count, args.rate, args.time)
        name = "L" if args.count is None else "lambda" if args.rate is None else "W"
        print(f"{name} = {value:g}")
    elif args.cmd == "buffer":
        print(f"{fmt_size(buffer_bytes(parse_rate(args.rate), parse_time(args.delay)))} queued")
    else:
        print(f"queueing delay = {fmt_time(delay_from_buffer(parse_rate(args.rate), args.bytes))}")


if __name__ == "__main__":
    main()
