"""M/G/1 and G/G/1 waiting times: why packet-size and burst variability matter.

The Pollaczek-Khinchine formula gives the mean wait in queue of an M/G/1
system with utilisation ``rho``, mean service time ``E[S]`` and squared
coefficient of variation of service ``cs2 = Var[S] / E[S]^2``::

    Wq = rho / (1 - rho) * (1 + cs2) / 2 * E[S]

``cs2 = 1`` is M/M/1, ``cs2 = 0`` is M/D/1 (fixed-size cells: half the
wait). Kingman's approximation extends it to bursty arrivals with arrival
variability ``ca2``::

    Wq ~ rho / (1 - rho) * (ca2 + cs2) / 2 * E[S]

For a packet mix, ``E[S]`` and ``cs2`` come from the size distribution at
the link rate.

Usage::

    python -m netcalc.queueing.mg1 wait --rate 10G --load 0.7 --size 1000 --cs2 0
    python -m netcalc.queueing.mg1 mix --rate 10G --load 0.7 64:7 576:4 1500:1
    python -m netcalc.queueing.mg1 kingman --rate 10G --load 0.7 --size 1000 --ca2 4 --cs2 1
"""

import argparse

from netcalc.units import fmt_time, parse_rate


def pk_wait(utilization, mean_service_s, cs2=1.0):
    """Pollaczek-Khinchine mean wait in queue (s).

    >>> round(pk_wait(0.8, 1.0, cs2=1.0), 3)
    4.0
    """
    if not 0 <= utilization < 1:
        raise ValueError("utilization must be in [0, 1)")
    return utilization / (1 - utilization) * (1 + cs2) / 2 * mean_service_s


def md1_wait(utilization, service_s):
    """Mean wait (s) of an M/D/1 queue (constant service time)."""
    return pk_wait(utilization, service_s, cs2=0.0)


def kingman_wait(utilization, mean_service_s, ca2, cs2):
    """Kingman's G/G/1 approximation of the mean wait in queue (s)."""
    if not 0 <= utilization < 1:
        raise ValueError("utilization must be in [0, 1)")
    return utilization / (1 - utilization) * (ca2 + cs2) / 2 * mean_service_s


def size_mix_moments(mix):
    """Mean size and squared coefficient of variation of ``{bytes: weight}``.

    >>> size_mix_moments({1000: 1})
    (1000.0, 0.0)
    """
    total = sum(mix.values())
    mean = sum(s * w for s, w in mix.items()) / total
    second = sum(s * s * w for s, w in mix.items()) / total
    return mean, second / mean ** 2 - 1


def mix_wait(link_bps, utilization, mix):
    """Mean M/G/1 queueing delay (s) for a packet-size mix on a link."""
    mean_bytes, cs2 = size_mix_moments(mix)
    return pk_wait(utilization, mean_bytes * 8 / link_bps, cs2)


def parse_mix(items):
    """Parse ``["64:7", "1500:1"]`` into ``{64: 7.0, 1500: 1.0}``."""
    return {int(s): float(w) for s, w in (item.split(":", 1) for item in items)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("wait", help="M/G/1 wait for one packet size")
    p.add_argument("--rate", required=True)
    p.add_argument("--load", type=float, required=True)
    p.add_argument("--size", type=float, required=True, help="mean packet bytes")
    p.add_argument("--cs2", type=float, default=1.0, help="service-time SCV (0 = fixed size)")
    p = sub.add_parser("mix", help="M/G/1 wait for a packet-size mix")
    p.add_argument("--rate", required=True)
    p.add_argument("--load", type=float, required=True)
    p.add_argument("mix", nargs="+", help="bytes:weight, e.g. 64:7 576:4 1500:1")
    p = sub.add_parser("kingman", help="G/G/1 wait with bursty arrivals")
    p.add_argument("--rate", required=True)
    p.add_argument("--load", type=float, required=True)
    p.add_argument("--size", type=float, required=True)
    p.add_argument("--ca2", type=float, required=True, help="arrival SCV (1 = Poisson)")
    p.add_argument("--cs2", type=float, default=1.0)
    args = parser.parse_args(argv)

    rate = parse_rate(args.rate)
    if args.cmd == "wait":
        print(f"mean queueing delay = {fmt_time(pk_wait(args.load, args.size * 8 / rate, args.cs2))}")
    elif args.cmd == "mix":
        mix = parse_mix(args.mix)
        mean, cs2 = size_mix_moments(mix)
        print(f"mean {mean:.1f} B, cs2 {cs2:.3f}, "
              f"mean queueing delay = {fmt_time(mix_wait(rate, args.load, mix))}")
    else:
        w = kingman_wait(args.load, args.size * 8 / rate, args.ca2, args.cs2)
        print(f"mean queueing delay ~ {fmt_time(w)}")


if __name__ == "__main__":
    main()
