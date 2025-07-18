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
