"""One-way latency budget: serialization, propagation, and per-hop delay.

End-to-end latency is the sum of four kinds of delay:

* **serialization**: clocking the bits of a packet onto the wire,
  ``bits / rate``; paid once per store-and-forward hop
* **propagation**: distance over the signal speed in the medium,
  about 4.9 us per km in fibre (refractive index ~1.468)
* **processing**: lookup and forwarding inside each device
* **queueing**: time spent waiting behind other packets

Usage::

    python -m netcalc.perf.latency serialization --size 1500 --rate 10G
    python -m netcalc.perf.latency propagation --km 100
    python -m netcalc.perf.latency path --size 9000 --rate 400G --hops 3 --km 2 --proc 600ns
"""

import argparse

from netcalc.units import (FIBER_REFRACTIVE_INDEX, SPEED_OF_LIGHT_M_S, fmt_time,
                           parse_rate, parse_size, parse_time)


def serialization_delay(size_bytes, rate_bps):
    """Seconds to clock ``size_bytes`` onto a link of ``rate_bps``.

    >>> serialization_delay(1500, 10e9)
    1.2e-06
    """
    return size_bytes * 8 / rate_bps


def propagation_delay(distance_km, refractive_index=FIBER_REFRACTIVE_INDEX):
    """Seconds for light to cover ``distance_km`` in a medium.

    Use ``refractive_index=1.0`` for free space / microwave links and
    about 1.5 for copper twinax (velocity factor ~0.66).
    """
    return distance_km * 1000 * refractive_index / SPEED_OF_LIGHT_M_S


def km_per_ms(refractive_index=FIBER_REFRACTIVE_INDEX):
    """Distance covered per millisecond in the medium (~204 km in fibre)."""
    return SPEED_OF_LIGHT_M_S / refractive_index / 1000 / 1000


def path_latency(size_bytes, rate_bps, hops=1, distance_km=0.0, processing_s=0.0,
                 queueing_s=0.0, cut_through=False):
    """One-way latency across ``hops`` links with the same rate.

    Store-and-forward pays serialization on every hop; cut-through switches
    pay it only once (at the first link). Returns a dict of components and
    their ``total``.
    """
    ser_hops = 1 if cut_through else hops
    parts = {
        "serialization": serialization_delay(size_bytes, rate_bps) * ser_hops,
        "propagation": propagation_delay(distance_km),
        "processing": processing_s * max(hops - 1, 0),
        "queueing": queueing_s,
    }
    parts["total"] = sum(parts.values())
    return parts


def rtt(one_way_s, return_one_way_s=None):
    """Round-trip time from one-way delays (symmetric if only one is given)."""
    return one_way_s + (one_way_s if return_one_way_s is None else return_one_way_s)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("serialization")
    p.add_argument("--size", required=True, help="packet size, e.g. 1500 or 9KB")
    p.add_argument("--rate", required=True, help="link rate, e.g. 10G")
    p = sub.add_parser("propagation")
    p.add_argument("--km", type=float, required=True)
    p.add_argument("--index", type=float, default=FIBER_REFRACTIVE_INDEX)
    p = sub.add_parser("path")
    p.add_argument("--size", required=True)
    p.add_argument("--rate", required=True)
    p.add_argument("--hops", type=int, default=1)
    p.add_argument("--km", type=float, default=0.0)
    p.add_argument("--proc", default="0", help="per-device processing time, e.g. 600ns")
    p.add_argument("--queue", default="0", help="total queueing delay")
    p.add_argument("--cut-through", action="store_true")
    args = parser.parse_args(argv)

    if args.cmd == "serialization":
        print(fmt_time(serialization_delay(parse_size(args.size), parse_rate(args.rate))))
    elif args.cmd == "propagation":
        d = propagation_delay(args.km, args.index)
        print(f"one-way {fmt_time(d)}, RTT {fmt_time(rtt(d))}")
    else:
        parts = path_latency(parse_size(args.size), parse_rate(args.rate), args.hops, args.km,
                             parse_time(args.proc), parse_time(args.queue), args.cut_through)
        for name, value in parts.items():
            print(f"{name:>14}: {fmt_time(value)}")


if __name__ == "__main__":
    main()
