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


def usable_hosts(prefixlen, version=4):
    """Usable host addresses in a prefix.

    IPv4 subtracts network and broadcast, except /31 (RFC 3021 point-to-point,
    2 hosts) and /32 (1 host). IPv6 has no broadcast, so all addresses count.
    """
    bits = 32 if version == 4 else 128
    total = 2 ** (bits - prefixlen)
    if version == 6 or prefixlen >= 31:
        return total
    return total - 2


def _host_bounds(net):
    if net.prefixlen >= 31:
        return str(net.network_address), str(net.broadcast_address)
    return str(net.network_address + 1), str(net.broadcast_address - 1)


def subnet_info(cidr):
    """Describe the network containing ``cidr`` (host bits are allowed)."""
    iface = ipaddress.ip_interface(cidr)
    net = iface.network
    info = {
        "address": str(iface.ip),
        "network": str(net.network_address),
        "prefix": net.prefixlen,
        "netmask": str(net.netmask),
        "total_addresses": net.num_addresses,
        "usable_hosts": usable_hosts(net.prefixlen, net.version),
        "scope": "private" if net.is_private else "public",
    }
    if net.version == 4:
        hosts = list(_host_bounds(net))
        info.update({
            "wildcard": str(net.hostmask),
            "broadcast": str(net.broadcast_address),
            "first_host": hosts[0],
            "last_host": hosts[1],
            "class": address_class(net.network_address),
        })
    else:
        info.update({
            "first_host": str(net.network_address),
            "last_host": str(net.broadcast_address),
        })
    return info


def prefix_for_hosts(hosts, version=4):
    """Longest prefix whose usable host count is at least ``hosts``."""
    bits = 32 if version == 4 else 128
    extra = 0 if version == 6 else 2
    host_bits = max(math.ceil(math.log2(hosts + extra)), 0)
    if host_bits > bits:
        raise ValueError("too many hosts for the address family")
    return bits - host_bits


def split(cidr, new_prefix):
    """Split a network into equal subnets of ``new_prefix``."""
    net = ipaddress.ip_network(cidr, strict=False)
    return [str(s) for s in net.subnets(new_prefix=new_prefix)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("info", help="describe a subnet")
    p.add_argument("cidr")
    p = sub.add_parser("split", help="split into smaller subnets")
    p.add_argument("cidr")
    p.add_argument("--prefix", type=int, required=True)
    p = sub.add_parser("hosts", help="prefix needed for N hosts")
    p.add_argument("hosts", type=int)
    p.add_argument("--v6", action="store_true")
    args = parser.parse_args(argv)

    if args.cmd == "info":
        for key, value in subnet_info(args.cidr).items():
            print(f"{key:>16}: {value}")
    elif args.cmd == "split":
        for s in split(args.cidr, args.prefix):
            print(s)
    else:
        version = 6 if args.v6 else 4
        prefix = prefix_for_hosts(args.hosts, version)
        print(f"/{prefix} ({usable_hosts(prefix, version)} usable hosts)")


if __name__ == "__main__":
    main()
