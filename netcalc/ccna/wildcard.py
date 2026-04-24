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


def range_to_entries(first, last):
    """Minimal list of ``(address, wildcard)`` ACL entries covering a range."""
    nets = ipaddress.summarize_address_range(ipaddress.IPv4Address(first),
                                             ipaddress.IPv4Address(last))
    return [(str(n.network_address), str(n.hostmask)) for n in nets]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("from-mask")
    p.add_argument("mask")
    p = sub.add_parser("to-mask")
    p.add_argument("wildcard")
    p = sub.add_parser("from-prefix")
    p.add_argument("prefix", type=int)
    p = sub.add_parser("match", help="test an address against an ACL entry")
    p.add_argument("address")
    p.add_argument("wildcard")
    p.add_argument("candidate")
    p = sub.add_parser("range", help="ACL entries for an address range")
    p.add_argument("first")
    p.add_argument("last")
    args = parser.parse_args(argv)

    if args.cmd == "from-mask":
        print(mask_to_wildcard(args.mask))
    elif args.cmd == "to-mask":
        print(wildcard_to_mask(args.wildcard))
    elif args.cmd == "from-prefix":
        print(prefix_to_wildcard(args.prefix))
    elif args.cmd == "match":
        hit = matches(args.address, args.wildcard, args.candidate)
        print(f"{args.candidate} {'matches' if hit else 'does not match'} "
              f"{args.address} {args.wildcard} ({match_count(args.wildcard)} addresses)")
    else:
        for address, wildcard in range_to_entries(args.first, args.last):
            print(f"permit ip {address} {wildcard} any")


if __name__ == "__main__":
    main()
