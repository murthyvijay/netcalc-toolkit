"""Size the back-end fabric and failure budget of a GPU training cluster.

Combines the AI fabric tools: leaf-spine sizing, data-parallel gradient
traffic, pipeline bubble, checkpoint size and the Young/Daly checkpoint
interval for the cluster's failure rate.

    python examples/ai_cluster_plan.py --gpus 2048 --radix 64 --params 70e9 --rate 400G
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netcalc.aifabric import checkpoint, parallelism, topology  # noqa: E402
from netcalc.units import fmt_size, fmt_time, parse_rate  # noqa: E402


def fabric_lines(gpus, radix):
    """Fabric sizing lines: two tiers if they fit, otherwise the three-tier limit."""
    try:
        plan = topology.leaf_spine_plan(gpus, radix)
    except ValueError:
        return [f"fabric             {gpus} GPUs exceed a two-tier radix-{radix} fabric; "
                f"three tiers reach {topology.three_tier_max_hosts(radix):,}"]
    return [f"fabric             {plan['leaves']} leaves + {plan['spines']} spines, "
            f"{topology.optics_count(plan['leaf_spine_links']):,} optics"]


def training_lines(gpus, params, rate_bps, tp=8, pp=8, microbatches=32):
    """Gradient traffic per step and pipeline efficiency for a 3D-parallel layout."""
    dp = max(gpus // (tp * pp), 1)
    shard = params / (tp * pp)
    grad_bytes = parallelism.dp_bytes_per_step(shard, 2, dp)
    return [
        f"layout             TP {tp} x PP {pp} x DP {dp}",
        f"gradient sync      {fmt_size(grad_bytes)} per GPU per step, "
        f"{fmt_time(parallelism.comm_time(grad_bytes, rate_bps))} at line rate",
        f"pipeline bubble    {parallelism.pipeline_bubble(pp, microbatches):.1%} "
        f"with {microbatches} micro-batches",
    ]


def resilience_lines(gpus, params, storage_bps, gpu_mtbf_hours=50000.0):
    """Checkpoint size and interval for the cluster's failure rate."""
    size = checkpoint.checkpoint_bytes(params)
    write = checkpoint.write_time(size, storage_bps)
    mtbf_s = checkpoint.job_mtbf_hours(gpu_mtbf_hours, gpus) * 3600
    tau = checkpoint.optimal_interval(write, mtbf_s)
    return [
        f"checkpoint         {fmt_size(size)}, {fmt_time(write)} to write",
        f"job MTBF           {fmt_time(mtbf_s)}; checkpoint every {fmt_time(tau)} "
        f"(~{checkpoint.wasted_fraction(tau, write, mtbf_s):.1%} of time lost)",
    ]
