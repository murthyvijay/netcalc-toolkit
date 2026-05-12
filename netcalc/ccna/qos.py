"""QoS math: queueing delay, CBWFQ shares, policing and shaping.

* **M/M/1 queue**: with arrival rate lambda and service rate mu
  (utilisation rho = lambda / mu) the mean wait in queue is
  ``rho / (mu - lambda)`` and the mean number queued ``rho^2 / (1 - rho)``.
  Delay explodes as rho approaches 1, which is why links are planned for
  well under 100 % utilisation.
* **CBWFQ**: each class gets its configured share of the link when
  congested; priority (LLQ) traffic is served first but policed.
* **Token bucket**: shaping interval ``Tc = Bc / CIR``; Cisco recommends a
  policer burst of 1.5 seconds of traffic (``Bc = CIR / 8 * 1.5`` bytes).

Usage::

    python -m netcalc.ccna.qos mm1 --rate 1G --load 0.8 --size 1000
    python -m netcalc.ccna.qos cbwfq --rate 10G VOICE=10 VIDEO=30 DATA=40
    python -m netcalc.ccna.qos shaper --cir 50M --bc 200000
"""

import argparse

from netcalc.units import fmt_rate, fmt_time, parse_rate, parse_size


def mm1(link_bps, utilization, packet_bytes):
    """M/M/1 queue statistics for a link at ``utilization`` (0..1)."""
    if not 0 <= utilization < 1:
        raise ValueError("utilization must be in [0, 1)")
    mu = link_bps / (packet_bytes * 8)
    lam = utilization * mu
    wait = utilization / (mu - lam)
    return {
        "service_time": 1 / mu,
        "queue_wait": wait,
        "system_time": wait + 1 / mu,
        "avg_queue_len": utilization ** 2 / (1 - utilization),
    }


def cbwfq_allocation(link_bps, shares_pct):
    """Guaranteed bandwidth per class from percentage shares (sum <= 100)."""
    total = sum(shares_pct.values())
    if total > 100:
        raise ValueError(f"class shares add up to {total} % (> 100 %)")
    alloc = {name: link_bps * pct / 100 for name, pct in shares_pct.items()}
    alloc["unallocated"] = link_bps * (100 - total) / 100
    return alloc


def shaping_interval(cir_bps, bc_bits):
    """Token bucket refill interval Tc = Bc / CIR (seconds)."""
    return bc_bits / cir_bps


def recommended_policer_burst(cir_bps, seconds=1.5):
    """Policer committed burst in bytes for ``seconds`` of traffic at CIR."""
    return cir_bps / 8 * seconds


def parse_shares(items):
    """``["VOICE=10", "DATA=40"] -> {"VOICE": 10.0, "DATA": 40.0}``."""
    return {k: float(v) for k, _, v in (i.partition("=") for i in items)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("mm1")
    p.add_argument("--rate", required=True)
    p.add_argument("--load", type=float, required=True)
    p.add_argument("--size", default="1000")
    p = sub.add_parser("cbwfq")
    p.add_argument("--rate", required=True)
    p.add_argument("classes", nargs="+", help="NAME=PERCENT")
    p = sub.add_parser("shaper")
    p.add_argument("--cir", required=True)
    p.add_argument("--bc", type=float, help="committed burst in bits")
    args = parser.parse_args(argv)

    if args.cmd == "mm1":
        stats = mm1(parse_rate(args.rate), args.load, parse_size(args.size))
        for key, value in stats.items():
            print(f"{key:>14}: {value:.3f}" if key == "avg_queue_len"
                  else f"{key:>14}: {fmt_time(value)}")
    elif args.cmd == "cbwfq":
        for name, bw in cbwfq_allocation(parse_rate(args.rate), parse_shares(args.classes)).items():
            print(f"{name:>12}: {fmt_rate(bw)}")
    else:
        cir = parse_rate(args.cir)
        print(f"recommended policer Bc: {recommended_policer_burst(cir):.0f} bytes")
        if args.bc:
            print(f"shaping interval Tc: {fmt_time(shaping_interval(cir, args.bc))}")


if __name__ == "__main__":
    main()
