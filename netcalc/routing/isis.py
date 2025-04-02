"""IS-IS addressing and metrics: NETs, system IDs, narrow vs wide metrics, LSP refresh.

* A **NET** (network entity title) is an NSAP with selector 00, written in
  dotted hex: ``49.0001.1921.6800.1001.00`` is AFI 49 (private), area
  0001, system ID 1921.6800.1001 and NSEL 00. A common convention derives
  the system ID from a loopback IPv4 address by zero-padding each octet to
  three digits (192.168.1.1 -> 192168001001 -> 1921.6800.1001).
* **Metrics**: narrow (original) metrics are 6 bits per interface (max 63)
  and 10 bits per path (max 1023), too small to express modern link speeds.
  Wide metrics (RFC 5305) allow 24 bits per interface (max 16,777,215).
  IS-IS has no automatic cost; operators often use ``reference / bandwidth``.
* **LSP refresh**: LSPs live for MaxAge (1200 s by default, up to 65535 s)
  and are refreshed before they expire (900 s by default), so a domain with
  N LSPs carries about ``N / refresh`` LSPs per second of background flooding.

Usage::

    python -m netcalc.routing.isis net 49.0001.1921.6800.1001.00
    python -m netcalc.routing.isis sysid 192.168.1.1 --area 49.0001
    python -m netcalc.routing.isis metric --rate 400G --reference 1T --style wide
    python -m netcalc.routing.isis refresh --lsps 5000 --refresh 900
"""

import argparse
import ipaddress
import math

from netcalc.units import parse_rate

NARROW_INTERFACE_MAX = 63
NARROW_PATH_MAX = 1023
WIDE_INTERFACE_MAX = 2 ** 24 - 1
DEFAULT_MAX_AGE_S = 1200
DEFAULT_REFRESH_S = 900


def parse_net(net):
    """Split a NET into area, system ID and selector.

    >>> parse_net("49.0001.1921.6800.1001.00")
    {'area': '49.0001', 'system_id': '1921.6800.1001', 'nsel': '00'}
    """
    parts = net.lower().split(".")
    if len(parts) < 5 or len(parts[-1]) != 2 or any(len(p) != 4 for p in parts[-4:-1]):
        raise ValueError(f"not a NET: {net!r}")
    return {"area": ".".join(parts[:-4]), "system_id": ".".join(parts[-4:-1]), "nsel": parts[-1]}


def system_id_from_ipv4(address):
    """System ID from an IPv4 loopback by padding each octet to three digits."""
    digits = "".join(f"{int(o):03d}" for o in str(ipaddress.IPv4Address(address)).split("."))
    return ".".join(digits[i:i + 4] for i in range(0, 12, 4))
