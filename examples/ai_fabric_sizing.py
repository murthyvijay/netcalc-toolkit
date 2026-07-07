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
