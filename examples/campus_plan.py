"""Plan a small campus: VLSM subnets, ACL wildcards and OSPF costs in one go.

    python examples/campus_plan.py 10.20.0.0/22 USERS=400 VOICE=200 SERVERS=60 MGMT=20
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netcalc.ccna import ospf, summarize, vlsm, wildcard  # noqa: E402
from netcalc.units import parse_rate  # noqa: E402
