"""Size a RoCE/Ultra Ethernet style backend fabric for one training job.

Answers in one run: how uneven ECMP is versus spraying for the job's flows,
the PFC headroom per port, the reorder buffer a multipath transport needs,
and how long one all-reduce takes.

    python examples/ai_fabric_sizing.py --gpus 512 --rate 400G --paths 64 --size 1GB
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netcalc.aifabric import collectives, loadbalance, mrc, roce  # noqa: E402
from netcalc.units import fmt_size, fmt_time, parse_rate, parse_size, parse_time  # noqa: E402


def fabric_summary(gpus, rate_bps, paths, size_bytes, skew_s=4e-6, cable_m=50):
    """Return a dict of the key sizing numbers."""
    flows = min(gpus, paths)
    ecmp = loadbalance.simulate_max_load(flows, paths, 1, trials=300)
    spray = loadbalance.simulate_max_load(flows, paths, 64, trials=300)
    return {
        "ecmp_efficiency": loadbalance.effective_throughput_fraction(ecmp),
        "spray_efficiency": loadbalance.effective_throughput_fraction(spray),
        "pfc_headroom": roce.pfc_headroom(rate_bps, cable_m),
        "reorder_buffer": mrc.reorder_buffer_bytes(rate_bps, skew_s, 4096),
        "allreduce_time": collectives.ring_allreduce_time(size_bytes, gpus, rate_bps, 5e-6),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--gpus", type=int, default=512)
    parser.add_argument("--rate", default="400G")
    parser.add_argument("--paths", type=int, default=64)
    parser.add_argument("--size", default="1GB")
    parser.add_argument("--skew", default="4us")
    args = parser.parse_args()
    s = fabric_summary(args.gpus, parse_rate(args.rate), args.paths, parse_size(args.size),
                       parse_time(args.skew))
    print(f"ECMP flow hashing efficiency : {s['ecmp_efficiency']:.0%}")
    print(f"packet spraying efficiency   : {s['spray_efficiency']:.0%}")
    print(f"PFC headroom per priority    : {fmt_size(s['pfc_headroom'])}")
    print(f"multipath reorder buffer     : {fmt_size(s['reorder_buffer'])}")
    print(f"ring all-reduce of {args.size:<9} : {fmt_time(s['allreduce_time'])}")


if __name__ == "__main__":
    main()
