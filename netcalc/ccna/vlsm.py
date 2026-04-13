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
