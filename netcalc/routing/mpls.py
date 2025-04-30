"""MPLS and segment routing: label overhead, MTU, label space and LSP/session scale.

* Each MPLS label stack entry is 4 bytes: 20-bit label, 3-bit traffic class,
  bottom-of-stack bit and 8-bit TTL. Labels 0-15 are reserved, leaving
  ``2^20 - 16 = 1,048,560`` usable values per label space.
* A packet with N labels needs ``4 N`` extra bytes of MTU. SR-MPLS traffic
  engineering pushes one label per segment, so the maximum SID depth (MSD)
  of the head-end hardware limits explicit paths.
* A full mesh of RSVP-TE tunnels between n PEs needs ``n (n - 1)``
  unidirectional LSPs; LDP needs a session per IGP neighbour plus targeted
  sessions; SR needs no per-LSP state in the core at all.

Usage::

    python -m netcalc.routing.mpls stack --labels 3 --payload-mtu 1500
    python -m netcalc.routing.mpls mesh --pes 200
    python -m netcalc.routing.mpls label 16005 --tc 5 --bos --ttl 64
"""

import argparse

LABEL_BYTES = 4
RESERVED_LABELS = 16
LABEL_SPACE = 2 ** 20


def stack_overhead(labels):
    """Bytes added by a label stack of ``labels`` entries."""
    return labels * LABEL_BYTES
