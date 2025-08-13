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
