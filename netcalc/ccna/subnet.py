"""IPv4/IPv6 subnet calculator.

Everything the CCNA subnetting chapter asks for: network and broadcast
address, usable host range, mask and wildcard, address class and scope, the
prefix that fits a host count, and splitting a block into smaller subnets.

Usage::

    python -m netcalc.ccna.subnet info 192.168.10.77/26
    python -m netcalc.ccna.subnet split 10.0.0.0/22 --prefix 24
    python -m netcalc.ccna.subnet hosts 500
    python -m netcalc.ccna.subnet info 2001:db8:abcd::/48
"""

import argparse
import ipaddress
import math


def address_class(addr):
    """Classful class letter of an IPv4 address (A-E)."""
    first = int(ipaddress.IPv4Address(addr)) >> 24
    if first < 128:
        return "A"
    if first < 192:
        return "B"
    if first < 224:
        return "C"
    if first < 240:
        return "D"
    return "E"
