"""Route summarization (supernetting).

Two answers are useful when summarizing:

* the **exact** aggregate: the fewest prefixes that cover precisely the
  given networks and nothing else
* the **single summary**: the one prefix that covers all of them, plus how
  much extra address space it advertises that was not in the list

Usage::

    python -m netcalc.ccna.summarize 172.16.0.0/24 172.16.1.0/24 172.16.2.0/24 172.16.3.0/24
    python -m netcalc.ccna.summarize 10.1.4.0/24 10.1.5.0/24 10.1.7.0/24
"""

import argparse
import ipaddress


def exact_aggregate(networks):
    """Collapse networks into the minimal list of covering prefixes."""
    nets = [ipaddress.ip_network(n, strict=False) for n in networks]
    return [str(n) for n in ipaddress.collapse_addresses(nets)]


def single_summary(networks):
    """Smallest single prefix containing every network."""
    nets = [ipaddress.ip_network(n, strict=False) for n in networks]
    low = min(int(n.network_address) for n in nets)
    high = max(int(n.broadcast_address) for n in nets)
    bits = nets[0].max_prefixlen
    prefix = bits - (low ^ high).bit_length()
    return str(ipaddress.ip_network((low, prefix), strict=False))


def summary_waste(networks):
    """Addresses covered by :func:`single_summary` that are not in ``networks``."""
    summary = ipaddress.ip_network(single_summary(networks))
    covered = sum(ipaddress.ip_network(n).num_addresses for n in exact_aggregate(networks))
    return summary.num_addresses - covered
