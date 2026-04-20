"""Wildcard masks for ACLs and OSPF network statements.

A wildcard mask is the bitwise inverse of a subnet mask: 0 bits must match,
1 bits are "don't care". Cisco ACLs also allow non-contiguous wildcards
(for example matching only odd third octets), which this module handles.

Usage::

    python -m netcalc.ccna.wildcard from-mask 255.255.255.224
    python -m netcalc.ccna.wildcard from-prefix 20
    python -m netcalc.ccna.wildcard match 10.1.0.0 0.0.254.255 10.1.7.9
    python -m netcalc.ccna.wildcard range 172.16.4.0 172.16.7.255
"""

import argparse
import ipaddress


def _int(addr):
    return int(ipaddress.IPv4Address(addr))


def _ip(value):
    return str(ipaddress.IPv4Address(value))


def mask_to_wildcard(mask):
    """``255.255.255.224 -> 0.0.0.31``."""
    return _ip(_int(mask) ^ 0xFFFFFFFF)


def wildcard_to_mask(wildcard):
    """``0.0.0.31 -> 255.255.255.224`` (only for contiguous wildcards)."""
    if not is_contiguous(wildcard):
        raise ValueError("non-contiguous wildcard has no subnet-mask equivalent")
    return _ip(_int(wildcard) ^ 0xFFFFFFFF)


def prefix_to_wildcard(prefixlen):
    """``/20 -> 0.0.15.255``."""
    return _ip((1 << (32 - prefixlen)) - 1)


def is_contiguous(wildcard):
    """True when the 1 bits of the wildcard are all at the low end."""
    w = _int(wildcard)
    return (w & (w + 1)) == 0


def matches(address, wildcard, candidate):
    """Does ``candidate`` match the ACL entry ``address wildcard``?"""
    care = _int(wildcard) ^ 0xFFFFFFFF
    return (_int(address) & care) == (_int(candidate) & care)


def match_count(wildcard):
    """Number of addresses an ACL entry with this wildcard matches."""
    return 2 ** bin(_int(wildcard)).count("1")
