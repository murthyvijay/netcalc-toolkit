"""IPv6 addressing helpers: EUI-64, link-local, solicited-node multicast and prefix math.

* **Modified EUI-64** (RFC 4291): split the 48-bit MAC in half, insert
  ``ff:fe`` and flip the universal/local bit (0x02 of the first octet).
  ``00:1b:44:11:3a:b7`` becomes interface ID ``021b:44ff:fe11:3ab7``.
* **Link-local** addresses are ``fe80::/64`` plus an interface ID.
* **Solicited-node multicast** (used by neighbour discovery instead of ARP
  broadcast) is ``ff02::1:ff00:0/104`` plus the low 24 bits of the address,
  and maps to the Ethernet multicast MAC ``33:33`` + the low 32 bits.
* A /48 site holds ``2^(64-48) = 65,536`` /64 subnets.

Usage::

    python -m netcalc.protocols.ipv6 eui64 00:1b:44:11:3a:b7 --prefix 2001:db8:1:1::/64
    python -m netcalc.protocols.ipv6 nd 2001:db8::1:2:3
    python -m netcalc.protocols.ipv6 subnets 2001:db8::/48 --new-prefix 64
"""

import argparse
import ipaddress


def _mac_bytes(mac):
    digits = "".join(c for c in mac if c.isalnum())
    if len(digits) != 12:
        raise ValueError(f"not a MAC address: {mac!r}")
    return bytes.fromhex(digits)


def eui64_interface_id(mac):
    """Modified EUI-64 interface identifier (64-bit int) from a MAC address."""
    b = bytearray(_mac_bytes(mac))
    b[0] ^= 0x02
    return int.from_bytes(bytes(b[:3]) + b"\xff\xfe" + bytes(b[3:]), "big")


def eui64_address(prefix, mac):
    """SLAAC address of ``mac`` in a /64 ``prefix``.

    >>> str(eui64_address("2001:db8:1:1::/64", "00:1b:44:11:3a:b7"))
    '2001:db8:1:1:21b:44ff:fe11:3ab7'
    """
    net = ipaddress.IPv6Network(prefix)
    if net.prefixlen != 64:
        raise ValueError("EUI-64 needs a /64 prefix")
    return net.network_address + eui64_interface_id(mac)


def link_local(mac):
    """fe80::/64 link-local address derived from a MAC address."""
    return eui64_address("fe80::/64", mac)


def solicited_node(address):
    """Solicited-node multicast group of an IPv6 address.

    >>> str(solicited_node("2001:db8::1:2:3"))
    'ff02::1:ff02:3'
    """
    low24 = int(ipaddress.IPv6Address(address)) & 0xFFFFFF
    return ipaddress.IPv6Address(int(ipaddress.IPv6Address("ff02::1:ff00:0")) | low24)


def multicast_mac(group):
    """Ethernet MAC for an IPv6 multicast group: ``33:33`` + low 32 bits."""
    low32 = int(ipaddress.IPv6Address(group)) & 0xFFFFFFFF
    return "33:33:" + ":".join(f"{b:02x}" for b in low32.to_bytes(4, "big"))


def subnet_count(prefix, new_prefix):
    """How many subnets of length ``new_prefix`` fit in ``prefix``."""
    net = ipaddress.IPv6Network(prefix)
    if new_prefix < net.prefixlen:
        raise ValueError("new prefix must be longer")
    return 2 ** (new_prefix - net.prefixlen)


def nth_subnet(prefix, new_prefix, n):
    """The ``n``-th (0-based) subnet of length ``new_prefix`` inside ``prefix``."""
    net = ipaddress.IPv6Network(prefix)
    size = 2 ** (128 - new_prefix)
    return ipaddress.IPv6Network((int(net.network_address) + n * size, new_prefix))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("eui64", help="EUI-64 interface ID, SLAAC and link-local address")
    p.add_argument("mac")
    p.add_argument("--prefix", default=None, help="a /64 to build the SLAAC address in")
    p = sub.add_parser("nd", help="solicited-node group and multicast MAC")
    p.add_argument("address")
    p = sub.add_parser("subnets", help="count and list subnets")
    p.add_argument("prefix")
    p.add_argument("--new-prefix", type=int, default=64)
    p.add_argument("--show", type=int, default=4, help="how many to list")
    args = parser.parse_args(argv)

    if args.cmd == "eui64":
        iid = eui64_interface_id(args.mac)
        groups = [f"{(iid >> s) & 0xFFFF:04x}" for s in (48, 32, 16, 0)]
        print(f"interface ID {':'.join(groups)}")
        print(f"link-local   {link_local(args.mac)}")
        if args.prefix:
            print(f"SLAAC        {eui64_address(args.prefix, args.mac)}")
    elif args.cmd == "nd":
        group = solicited_node(args.address)
        print(f"solicited-node {group}, MAC {multicast_mac(group)}")
    else:
        count = subnet_count(args.prefix, args.new_prefix)
        print(f"{count:,} /{args.new_prefix} subnets in {args.prefix}")
        for i in range(min(args.show, count)):
            print(f"  {nth_subnet(args.prefix, args.new_prefix, i)}")


if __name__ == "__main__":
    main()
