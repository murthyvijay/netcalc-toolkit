"""VLSM (variable-length subnet mask) allocator.

Given an address block and a list of segments with host counts, allocate
the largest segments first so every subnet stays aligned, exactly as done
by hand in CCNA labs.

Usage::

    python -m netcalc.ccna.vlsm 192.168.1.0/24 SALES=100 ENG=50 HR=20 WAN1=2 WAN2=2
"""

import argparse
import ipaddress

from netcalc.ccna.subnet import prefix_for_hosts, usable_hosts


def allocate(block, requirements):
    """Allocate subnets for ``requirements`` (a dict of name -> hosts).

    Returns a list of dicts in allocation order and raises ``ValueError``
    when the block is too small.
    """
    base = ipaddress.ip_network(block, strict=False)
    ordered = sorted(requirements.items(), key=lambda kv: kv[1], reverse=True)
    cursor = int(base.network_address)
    end = int(base.broadcast_address)
    plan = []
    for name, hosts in ordered:
        prefix = prefix_for_hosts(hosts, base.version)
        if prefix < base.prefixlen:
            raise ValueError(f"{name} needs /{prefix}, larger than the block {block}")
        size = 2 ** (base.max_prefixlen - prefix)
        cursor = -(-cursor // size) * size  # align up to the subnet size
        if cursor + size - 1 > end:
            raise ValueError(f"block {block} exhausted while allocating {name}")
        net = ipaddress.ip_network((cursor, prefix))
        plan.append({
            "name": name,
            "needed": hosts,
            "subnet": str(net),
            "usable": usable_hosts(prefix, base.version),
            "mask": str(net.netmask),
        })
        cursor += size
    return plan


def utilization(block, plan):
    """Fraction of the block's addresses consumed by the plan."""
    base = ipaddress.ip_network(block, strict=False)
    used = sum(ipaddress.ip_network(p["subnet"]).num_addresses for p in plan)
    return used / base.num_addresses
