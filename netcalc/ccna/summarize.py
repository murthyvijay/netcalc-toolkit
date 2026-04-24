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
