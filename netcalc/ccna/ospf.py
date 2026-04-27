"""OSPF interface cost and path cost.

OSPF derives interface cost from bandwidth::

    cost = max(1, floor(reference_bandwidth / interface_bandwidth))

Cisco's default reference bandwidth is 100 Mbps, so every link at
100 Mbps or faster gets cost 1 and OSPF cannot tell 1G from 400G. Raise
``auto-cost reference-bandwidth`` (identically on every router) above the
fastest link you will ever deploy.

Usage::

    python -m netcalc.ccna.ospf cost 10G --ref 100G
    python -m netcalc.ccna.ospf table --ref 400G
    python -m netcalc.ccna.ospf path 10G 10G 1G --ref 100G
"""

import argparse

from netcalc.units import fmt_rate, parse_rate

DEFAULT_REF_BPS = 100e6
COMMON_RATES = ["10M", "100M", "1G", "10G", "25G", "40G", "100G", "400G", "800G"]
MAX_COST = 65535
