"""ECMP flow hashing vs packet spraying: collisions and load imbalance.

AI training traffic is a few very large, long-lived flows ("elephants").
Classic ECMP hashes each flow onto one path, so with F flows over P equal
paths some paths get two or more flows while others idle. Packet spraying
(as in Ultra Ethernet and multipath RDMA transports) spreads each flow's
packets over all paths, making the load almost perfectly even.

This module gives closed-form collision probabilities and seeded Monte Carlo
estimates of the worst-path load, so results are reproducible.

Usage::

    python -m netcalc.aifabric.loadbalance collide --flows 8 --paths 16
    python -m netcalc.aifabric.loadbalance imbalance --flows 64 --paths 64
    python -m netcalc.aifabric.loadbalance imbalance --flows 64 --paths 64 --spray 256
"""

import argparse
import math
import random


def collision_probability(flows, paths):
    """Probability that at least two of ``flows`` hash onto the same path.

    The birthday problem: ``1 - P! / ((P - F)! * P^F)``.
    """
    if flows > paths:
        return 1.0
    log_no_collision = (math.lgamma(paths + 1) - math.lgamma(paths - flows + 1)
                        - flows * math.log(paths))
    return 1 - math.exp(log_no_collision)


def expected_idle_paths(flows, paths):
    """Expected number of paths that receive no flow: ``P (1 - 1/P)^F``."""
    return paths * (1 - 1 / paths) ** flows


def simulate_max_load(flows, paths, units_per_flow=1, trials=2000, seed=1):
    """Mean of the busiest path's load divided by the ideal (even) load.

    ``units_per_flow=1`` models flow-level ECMP; a larger value models
    spraying each flow as that many independently hashed packets or
    sub-flows (for example several queue pairs per connection).
    """
    rng = random.Random(seed)
    ideal = flows * units_per_flow / paths
    total = 0.0
    for _ in range(trials):
        load = [0] * paths
        for _ in range(flows * units_per_flow):
            load[rng.randrange(paths)] += 1
        total += max(load) / ideal
    return total / trials


def effective_throughput_fraction(max_load_ratio):
    """Fraction of fabric bandwidth usable when the job runs at the slowest path.

    Synchronous collectives finish when the most loaded path finishes, so the
    useful throughput is ``1 / max_load_ratio`` of the ideal.
    """
    return 1 / max_load_ratio


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("collide")
    p.add_argument("--flows", type=int, required=True)
    p.add_argument("--paths", type=int, required=True)
    p = sub.add_parser("imbalance")
    p.add_argument("--flows", type=int, required=True)
    p.add_argument("--paths", type=int, required=True)
    p.add_argument("--spray", type=int, default=1, help="packets/sub-flows per flow")
    p.add_argument("--trials", type=int, default=2000)
    p.add_argument("--seed", type=int, default=1)
    args = parser.parse_args(argv)

    if args.cmd == "collide":
        print(f"P(collision) = {collision_probability(args.flows, args.paths):.2%}")
        print(f"expected idle paths = {expected_idle_paths(args.flows, args.paths):.2f}")
    else:
        ratio = simulate_max_load(args.flows, args.paths, args.spray, args.trials, args.seed)
        print(f"busiest path carries {ratio:.2f}x the even share; "
              f"effective throughput {effective_throughput_fraction(ratio):.1%}")


if __name__ == "__main__":
    main()
