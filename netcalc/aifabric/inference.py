"""LLM inference traffic: KV-cache size, prefill-to-decode transfer and decode throughput.

* **KV cache**: every token keeps a key and a value vector per layer and
  per KV head::

      bytes/token = 2 * layers * kv_heads * head_dim * bytes_per_value

  A 70B-class model with 80 layers, 8 KV heads (grouped-query attention)
  and head_dim 128 in 16-bit needs 320 KiB per token, so a 32k-token
  context is 10 GiB.
* **Disaggregated serving** runs prefill and decode on different GPUs, so
  the whole prompt's KV cache crosses the fabric before the first decoded
  token: ``latency + prompt_tokens * bytes/token / bandwidth``.
* **Decode is memory-bound**: each step streams all weights plus every
  active sequence's KV cache from HBM, so tokens/s per sequence is about
  ``HBM bandwidth / (weight bytes + batch * KV bytes)``.

Usage::

    python -m netcalc.aifabric.inference kv --layers 80 --kv-heads 8 --head-dim 128 --tokens 32768
    python -m netcalc.aifabric.inference transfer --layers 80 --kv-heads 8 --head-dim 128 --tokens 8192 --bw 400G
    python -m netcalc.aifabric.inference decode --params 70e9 --bytes 2 --hbm 3.35T --batch 16 --context 4096 --layers 80 --kv-heads 8 --head-dim 128
"""

import argparse

from netcalc.units import fmt_size, fmt_time, parse_rate, parse_size, parse_time


def kv_bytes_per_token(layers, kv_heads, head_dim, bytes_per_value=2):
    """KV-cache bytes per token.

    >>> kv_bytes_per_token(80, 8, 128)
    327680
    """
    return 2 * layers * kv_heads * head_dim * bytes_per_value


def kv_cache_bytes(tokens, layers, kv_heads, head_dim, bytes_per_value=2, batch=1):
    """KV-cache bytes for ``batch`` sequences of ``tokens`` tokens."""
    return batch * tokens * kv_bytes_per_token(layers, kv_heads, head_dim, bytes_per_value)


def kv_transfer_time(prompt_tokens, bytes_per_token, bw_bps, latency_s=0.0):
    """Seconds to ship a prompt's KV cache from a prefill GPU to a decode GPU."""
    return latency_s + prompt_tokens * bytes_per_token * 8 / bw_bps


def decode_tokens_per_second(weight_bytes, hbm_Bps, batch=1, kv_bytes_per_seq=0.0):
    """Memory-bound decode rate: ``(per sequence, aggregate)`` tokens per second."""
    per_step = weight_bytes + batch * kv_bytes_per_seq
    per_seq = hbm_Bps / per_step
    return per_seq, per_seq * batch


def max_batch_for_memory(hbm_capacity_bytes, weight_bytes, kv_bytes_per_seq):
    """Most sequences whose KV cache fits next to the weights in HBM."""
    free = hbm_capacity_bytes - weight_bytes
    return max(int(free // kv_bytes_per_seq), 0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    def model_args(p):
        p.add_argument("--layers", type=int, required=True)
        p.add_argument("--kv-heads", type=int, required=True)
        p.add_argument("--head-dim", type=int, required=True)
        p.add_argument("--kv-bytes", type=float, default=2, help="bytes per cached value")

    p = sub.add_parser("kv", help="KV-cache size")
    model_args(p)
    p.add_argument("--tokens", type=int, required=True)
    p.add_argument("--batch", type=int, default=1)
    p = sub.add_parser("transfer", help="prefill to decode KV transfer time")
    model_args(p)
    p.add_argument("--tokens", type=int, required=True)
    p.add_argument("--bw", required=True)
    p.add_argument("--latency", default="10us")
    p = sub.add_parser("decode", help="memory-bound decode throughput")
    model_args(p)
    p.add_argument("--params", type=float, required=True)
    p.add_argument("--bytes", type=float, default=2, help="bytes per weight")
    p.add_argument("--hbm", required=True, help="HBM bandwidth in bytes/s, e.g. 3.35T")
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--context", type=int, default=0, help="tokens of context per sequence")
    args = parser.parse_args(argv)

    per_token = kv_bytes_per_token(args.layers, args.kv_heads, args.head_dim, args.kv_bytes)
    if args.cmd == "kv":
        total = args.batch * args.tokens * per_token
        print(f"{fmt_size(per_token)} per token; {fmt_size(total)} for {args.batch} x {args.tokens} tokens")
    elif args.cmd == "transfer":
        t = kv_transfer_time(args.tokens, per_token, parse_rate(args.bw), parse_time(args.latency))
        print(f"{fmt_size(args.tokens * per_token)} of KV cache moves in {fmt_time(t)}")
    else:
        per_seq, total = decode_tokens_per_second(args.params * args.bytes, parse_size(args.hbm),
                                                  args.batch, args.context * per_token)
        print(f"{per_seq:.1f} tokens/s per sequence, {total:.0f} tokens/s aggregate")


if __name__ == "__main__":
    main()
