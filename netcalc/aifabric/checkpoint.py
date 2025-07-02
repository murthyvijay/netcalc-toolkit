"""Checkpointing and failures at scale: checkpoint size, write time and the optimal interval.

* **Checkpoint size**: mixed-precision Adam keeps bf16 weights (2 B), fp32
  master weights (4 B) and two fp32 moments (4 + 4 B), about 14 bytes per
  parameter, so a 70B model checkpoints roughly 1 TB.
* **Failures**: with N components each of mean time between failures M,
  the job sees a failure every ``M / N`` on average, and the probability of
  running ``T`` hours untouched is ``exp(-N T / M)``.
* **Young/Daly interval**: checkpointing every ``tau = sqrt(2 * delta * M_job)``
  (delta = time to write one checkpoint) minimises lost work. The expected
  fraction of time wasted is about ``delta / tau + (tau / 2 + R) / M_job``
  with restart time R.

Usage::

    python -m netcalc.aifabric.checkpoint size --params 70e9 --bw 200G
    python -m netcalc.aifabric.checkpoint interval --write 60s --gpus 16384 --mtbf 50000
    python -m netcalc.aifabric.checkpoint interruption --gpus 16384 --mtbf 50000 --hours 24
"""

import argparse
import math

from netcalc.units import fmt_size, fmt_time, parse_rate, parse_time

ADAM_MIXED_BYTES_PER_PARAM = 14


def checkpoint_bytes(params, bytes_per_param=ADAM_MIXED_BYTES_PER_PARAM):
    """Checkpoint size in bytes.

    >>> checkpoint_bytes(70e9)
    980000000000.0
    """
    return params * bytes_per_param


def write_time(nbytes, storage_bps):
    """Seconds to write a checkpoint at an aggregate storage bandwidth."""
    return nbytes * 8 / storage_bps


def job_mtbf_hours(component_mtbf_hours, components):
    """Mean time between failures (h) of a job spanning ``components`` parts."""
    return component_mtbf_hours / components


def interruption_probability(components, component_mtbf_hours, duration_hours):
    """Probability that at least one component fails during ``duration_hours``."""
    return 1 - math.exp(-components * duration_hours / component_mtbf_hours)


def optimal_interval(checkpoint_s, job_mtbf_s):
    """Young/Daly checkpoint interval (s): ``sqrt(2 * delta * MTBF)``."""
    return math.sqrt(2 * checkpoint_s * job_mtbf_s)


def wasted_fraction(interval_s, checkpoint_s, job_mtbf_s, restart_s=0.0):
    """Approximate fraction of wall-clock time lost to checkpoints, rework and restarts."""
    return checkpoint_s / interval_s + (interval_s / 2 + restart_s) / job_mtbf_s


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("size", help="checkpoint size and write time")
    p.add_argument("--params", type=float, required=True)
    p.add_argument("--bytes-per-param", type=float, default=ADAM_MIXED_BYTES_PER_PARAM)
    p.add_argument("--bw", default="200G", help="aggregate storage write bandwidth")
    p = sub.add_parser("interval", help="Young/Daly checkpoint interval")
    p.add_argument("--write", required=True, help="checkpoint write time, e.g. 60s")
    p.add_argument("--gpus", type=int, required=True)
    p.add_argument("--mtbf", type=float, required=True, help="per-GPU (or per-node) MTBF in hours")
    p.add_argument("--restart", default="600s", help="restart time")
    p = sub.add_parser("interruption", help="chance of a failure during a run")
    p.add_argument("--gpus", type=int, required=True)
    p.add_argument("--mtbf", type=float, required=True)
    p.add_argument("--hours", type=float, required=True)
    args = parser.parse_args(argv)

    if args.cmd == "size":
        b = checkpoint_bytes(args.params, args.bytes_per_param)
        print(f"checkpoint {fmt_size(b)}, written in {fmt_time(write_time(b, parse_rate(args.bw)))}")
    elif args.cmd == "interval":
        delta = parse_time(args.write)
        mtbf_s = job_mtbf_hours(args.mtbf, args.gpus) * 3600
        tau = optimal_interval(delta, mtbf_s)
        waste = wasted_fraction(tau, delta, mtbf_s, parse_time(args.restart))
        print(f"job MTBF {fmt_time(mtbf_s)}; checkpoint every {fmt_time(tau)}; ~{waste:.1%} wasted")
    else:
        p = interruption_probability(args.gpus, args.mtbf, args.hours)
        print(f"P(at least one failure in {args.hours:g} h) = {p:.1%}")


if __name__ == "__main__":
    main()
