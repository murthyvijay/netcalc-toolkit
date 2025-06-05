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


def step_time(compute_s, comm_s, overlap=0.0):
    """Step time when a fraction ``overlap`` of communication hides behind compute."""
    exposed = comm_s * (1 - overlap)
    return compute_s + exposed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("dp", help="data-parallel gradient traffic")
    p.add_argument("--params", type=float, required=True)
    p.add_argument("--bytes", type=float, default=2, help="bytes per gradient value")
    p.add_argument("--ranks", type=int, required=True)
    p.add_argument("--bw", default="400G", help="per-rank network bandwidth")
    p = sub.add_parser("tp", help="tensor-parallel activation traffic")
    p.add_argument("--tokens", type=int, required=True, help="tokens per micro-batch")
    p.add_argument("--hidden", type=int, required=True)
    p.add_argument("--layers", type=int, required=True)
    p.add_argument("--tp", type=int, required=True)
    p.add_argument("--bytes", type=float, default=2)
    p.add_argument("--bw", default="3.6T", help="per-GPU scale-up bandwidth")
    p = sub.add_parser("pp", help="pipeline-parallel boundary traffic")
    p.add_argument("--tokens", type=int, required=True)
    p.add_argument("--hidden", type=int, required=True)
    p.add_argument("--bytes", type=float, default=2)
    p = sub.add_parser("bubble", help="pipeline bubble fraction")
    p.add_argument("--stages", type=int, required=True)
    p.add_argument("--microbatches", type=int, required=True)
    args = parser.parse_args(argv)

    if args.cmd == "dp":
        b = dp_bytes_per_step(args.params, args.bytes, args.ranks)
        print(f"{fmt_size(b)} per rank per step, {fmt_time(comm_time(b, parse_rate(args.bw)))} "
              f"at {args.bw}")
    elif args.cmd == "tp":
        b = tp_bytes_per_step(args.tokens, args.hidden, args.layers, args.tp, args.bytes)
        print(f"{fmt_size(b)} per rank per micro-batch, "
              f"{fmt_time(comm_time(b, parse_rate(args.bw)))} at {args.bw}")
    elif args.cmd == "pp":
        print(f"{fmt_size(pp_bytes_per_microbatch(args.tokens, args.hidden, args.bytes))} "
              f"per boundary per micro-batch")
    else:
        print(f"bubble = {pipeline_bubble(args.stages, args.microbatches):.1%} of each step")


if __name__ == "__main__":
    main()
