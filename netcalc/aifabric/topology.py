"""Leaf-spine and fat-tree sizing for GPU clusters.

* A **two-tier leaf-spine** built from radix-k switches, non-blocking,
  gives each leaf k/2 host ports and k/2 uplinks (one to each of k/2
  spines); each spine port feeds one leaf, so up to k leaves and ``k^2 / 2``
  hosts.
* A **three-tier fat tree** (k pods) reaches ``k^3 / 4`` hosts with
  ``5 k^2 / 4`` switches.
* **Oversubscription** ``= downlink capacity / uplink capacity`` trades
  switches and optics for contention; AI back-end fabrics are normally built
  1:1.
* **Rail-optimised** designs connect GPU i of every server to leaf i
  ("rail" i), so a server with 8 GPUs touches 8 leaves and same-rank
  traffic stays one hop away.

Usage::

    python -m netcalc.aifabric.topology max --radix 64
    python -m netcalc.aifabric.topology plan --hosts 2048 --radix 64
    python -m netcalc.aifabric.topology rails --servers 128 --gpus 8 --radix 64
"""

import argparse
import math
