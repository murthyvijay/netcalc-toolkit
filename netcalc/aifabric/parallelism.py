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
