"""NAT and CGNAT port planning: port blocks, subscribers per address and pool size.

A public IPv4 address has 65,536 ports per protocol, of which 1024-65535
(64,512) are normally available for translation. Carrier-grade NAT
(RFC 6888) gives each subscriber a deterministic or bulk-allocated **port
block**, so::

    subscribers per address = floor(64512 / ports per subscriber)
    addresses needed        = ceil(subscribers / subscribers per address)

Port blocks also cut logging: one log line per block allocation instead of
one per session. Sizing the block is a trade-off: too small and busy
households run out of ports (a modern home can hold several hundred to a few
thousand concurrent sessions), too large and the address pool must grow.

Usage::

    python -m netcalc.protocols.nat pool --subscribers 100000 --ports 1024
    python -m netcalc.protocols.nat block --sessions 900 --headroom 1.5
    python -m netcalc.protocols.nat deterministic --index 1234 --ports 2048 --base 203.0.113.0/24
"""

import argparse
import ipaddress
import math

FIRST_DYNAMIC_PORT = 1024
PORTS_PER_ADDRESS = 65536 - FIRST_DYNAMIC_PORT


def subscribers_per_address(ports_per_subscriber):
    """Subscribers that share one public address.

    >>> subscribers_per_address(1024)
    63
    """
    return PORTS_PER_ADDRESS // ports_per_subscriber
