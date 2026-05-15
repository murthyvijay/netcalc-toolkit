"""Header overhead, wire efficiency and goodput for common protocol stacks.

Every Ethernet frame on the wire costs more than its payload:

==========================  =====  ======================================
item                        bytes  note
==========================  =====  ======================================
preamble + SFD              8      not counted in "frame size"
Ethernet header             14     +4 per 802.1Q tag
FCS                         4
inter-frame gap             12     minimum idle between frames
==========================  =====  ======================================

so a minimum 64-byte frame occupies 84 byte-times and a 10G link carries
at most 14.88 million of them per second.

A *stack* is a list of layer names from outer to inner, for example
``["eth", "ipv4", "udp", "vxlan", "eth", "ipv4", "tcp"]``.

Usage::

    python -m netcalc.protocols.overhead goodput --payload 1460 --stack eth,ipv4,tcp --rate 10G
    python -m netcalc.protocols.overhead goodput --payload 4096 --stack roce --rate 400G
    python -m netcalc.protocols.overhead pps --frame 64 --rate 100G
    python -m netcalc.protocols.overhead stacks
"""

import argparse

from netcalc.units import fmt_rate, parse_rate

ETH_WIRE_EXTRA = 8 + 12  # preamble/SFD + inter-frame gap
ETH_MIN_FRAME = 64

HEADERS = {
    "eth": 14 + 4,      # header + FCS (outer Ethernet)
    "dot1q": 4,
    "qinq": 8,
    "mpls": 4,          # per label
    "ipv4": 20,
    "ipv6": 40,
    "tcp": 20,
    "tcp_ts": 32,       # TCP with the 12-byte timestamp option
    "udp": 8,
    "vxlan": 8,
    "geneve": 8,        # base header, options extra
    "gre": 4,
    "bth": 12,          # InfiniBand base transport header
    "reth": 16,         # RDMA extended transport header (first packet of a WRITE)
    "icrc": 4,          # invariant CRC
    "inner_eth": 14,    # encapsulated Ethernet header (no FCS)
}

STACKS = {
    "tcp": ["eth", "ipv4", "tcp"],
    "tcp6": ["eth", "ipv6", "tcp"],
    "tcp_ts": ["eth", "ipv4", "tcp_ts"],
    "udp": ["eth", "ipv4", "udp"],
    "vxlan": ["eth", "ipv4", "udp", "vxlan", "inner_eth", "ipv4", "tcp"],
    "roce": ["eth", "ipv4", "udp", "bth", "icrc"],
    "roce_write": ["eth", "ipv4", "udp", "bth", "reth", "icrc"],
    "roce6": ["eth", "ipv6", "udp", "bth", "icrc"],
}


def resolve_stack(stack):
    """Accept a stack name, a comma string or a list; return a list of layers."""
    if isinstance(stack, str):
        if stack in STACKS:
            return list(STACKS[stack])
        stack = stack.split(",")
    unknown = [layer for layer in stack if layer not in HEADERS]
    if unknown:
        raise ValueError(f"unknown layers: {unknown}")
    return list(stack)


def header_bytes(stack):
    """Bytes of headers and trailers in a stack (excluding preamble/IFG)."""
    return sum(HEADERS[layer] for layer in resolve_stack(stack))


def frame_bytes(payload, stack):
    """Ethernet frame size (header to FCS), padded to the 64-byte minimum."""
    return max(ETH_MIN_FRAME, payload + header_bytes(stack))


def wire_bytes(payload, stack):
    """Bytes of line time a packet occupies, including preamble and IFG."""
    return frame_bytes(payload, stack) + ETH_WIRE_EXTRA


def efficiency(payload, stack):
    """Fraction of the line rate that is application payload."""
    return payload / wire_bytes(payload, stack)


def goodput(payload, stack, rate_bps):
    """Application-layer throughput at full line rate (bps)."""
    return rate_bps * efficiency(payload, stack)
