"""Communication volume of data, tensor and pipeline parallelism.

Large training jobs split the model three ways, and each split has its own
traffic pattern on the fabric:

* **Data parallel (DP)**: every rank holds a full replica and all-reduces
  the gradients each step. With a ring or bandwidth-optimal all-reduce each
  rank sends ``2 (N - 1) / N * P * b`` bytes for P parameters of b bytes.
* **Tensor parallel (TP)**, Megatron style: each transformer layer does
  two all-reduces of the activations in the forward pass and two in the
  backward pass, each of ``tokens * hidden * b`` bytes, inside the TP group
  (usually kept on NVLink within a server).
* **Pipeline parallel (PP)**: each stage boundary sends activations forward
  and gradients backward, ``2 * tokens * hidden * b`` bytes per micro-batch.
  The schedule leaves a bubble of ``(p - 1) / (m + p - 1)`` of the step idle
  for p stages and m micro-batches.

Usage::

    python -m netcalc.aifabric.parallelism dp --params 70e9 --bytes 2 --ranks 64 --bw 400G
    python -m netcalc.aifabric.parallelism tp --tokens 8192 --hidden 8192 --layers 80 --tp 8
    python -m netcalc.aifabric.parallelism bubble --stages 8 --microbatches 32
"""

import argparse

from netcalc.units import fmt_size, fmt_time, parse_rate


def allreduce_bytes_per_rank(message_bytes, ranks):
    """Bytes each rank sends in a bandwidth-optimal all-reduce."""
    return 2 * (ranks - 1) / ranks * message_bytes


def dp_bytes_per_step(params, bytes_per_param, ranks):
    """Gradient all-reduce bytes sent per rank per optimizer step.

    >>> dp_bytes_per_step(1e9, 2, 2)
    2000000000.0
    """
    return allreduce_bytes_per_rank(params * bytes_per_param, ranks)


def tp_bytes_per_step(tokens, hidden, layers, tp, bytes_per_value=2):
    """Activation all-reduce bytes per rank per step inside a TP group (4 per layer)."""
    if tp <= 1:
        return 0.0
    return 4 * layers * allreduce_bytes_per_rank(tokens * hidden * bytes_per_value, tp)


def pp_bytes_per_microbatch(tokens, hidden, bytes_per_value=2):
    """Bytes crossing one pipeline stage boundary per micro-batch (forward + backward)."""
    return 2 * tokens * hidden * bytes_per_value


def pipeline_bubble(stages, microbatches):
    """Idle fraction of a GPipe / 1F1B pipeline step.

    >>> round(pipeline_bubble(8, 32), 4)
    0.1795
    """
    return (stages - 1) / (microbatches + stages - 1)


def comm_time(nbytes, bw_bps, efficiency=1.0):
    """Seconds to move ``nbytes`` at ``bw_bps`` with a link efficiency factor."""
    return nbytes * 8 / (bw_bps * efficiency)
