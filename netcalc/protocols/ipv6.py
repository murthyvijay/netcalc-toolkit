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
