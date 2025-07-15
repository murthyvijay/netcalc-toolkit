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


def two_tier_max_hosts(radix):
    """Largest non-blocking leaf-spine: ``k^2 / 2`` hosts.

    >>> two_tier_max_hosts(64)
    2048
    """
    return radix * radix // 2


def three_tier_max_hosts(radix):
    """Largest non-blocking three-tier fat tree: ``k^3 / 4`` hosts."""
    return radix ** 3 // 4


def three_tier_switches(radix):
    """Switches in a full k-ary fat tree: ``5 k^2 / 4``."""
    return 5 * radix * radix // 4


def oversubscription(down_ports, up_ports, down_rate=1.0, up_rate=1.0):
    """Downlink to uplink capacity ratio of a leaf."""
    return (down_ports * down_rate) / (up_ports * up_rate)


def leaf_spine_plan(hosts, radix, oversub=1.0):
    """Leaves, spines and links for a two-tier fabric with a leaf oversubscription ratio."""
    down = math.floor(radix * oversub / (1 + oversub))
    up = radix - down
    leaves = math.ceil(hosts / down)
    if leaves > radix:
        raise ValueError(f"{hosts} hosts need {leaves} leaves; more than radix {radix}: use 3 tiers")
    spines = up
    return {"leaves": leaves, "spines": spines, "host_ports_per_leaf": down,
            "uplinks_per_leaf": up, "leaf_spine_links": leaves * up,
            "switches": leaves + spines}


def optics_count(links, transceivers_per_link=2):
    """Transceivers needed for ``links`` switch-to-switch links."""
    return links * transceivers_per_link


def rail_plan(servers, gpus_per_server, radix):
    """Rail-optimised layout: servers per rail group and leaves needed (one per rail per group)."""
    servers_per_group = radix // 2
    groups = math.ceil(servers / servers_per_group)
    return {"rails": gpus_per_server, "servers_per_group": servers_per_group,
            "groups": groups, "leaves": groups * gpus_per_server}


def bisection_bandwidth(hosts, host_rate_bps, oversub=1.0):
    """Bisection bandwidth (b/s) of a Clos fabric."""
    return hosts * host_rate_bps / 2 / oversub
