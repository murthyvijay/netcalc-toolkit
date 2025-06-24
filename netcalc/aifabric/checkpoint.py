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
