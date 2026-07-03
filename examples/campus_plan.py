"""Plan a small campus: VLSM subnets, ACL wildcards and OSPF costs in one go.

    python examples/campus_plan.py 10.20.0.0/22 USERS=400 VOICE=200 SERVERS=60 MGMT=20
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netcalc.ccna import ospf, summarize, vlsm, wildcard  # noqa: E402
from netcalc.units import parse_rate  # noqa: E402


def plan_campus(block, segments):
    """VLSM plan plus the wildcard each subnet needs in an ACL."""
    plan = vlsm.allocate(block, segments)
    for row in plan:
        row["wildcard"] = wildcard.mask_to_wildcard(row["mask"])
    return plan


def uplink_costs(reference="100G"):
    """OSPF costs for typical campus uplinks with a modern reference bandwidth."""
    return ospf.cost_table(parse_rate(reference), ["1G", "10G", "25G", "40G", "100G"])


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("block")
    parser.add_argument("segments", nargs="+", help="NAME=HOSTS")
    args = parser.parse_args()
    plan = plan_campus(args.block, vlsm.parse_requirements(args.segments))
    for row in plan:
        print(f"{row['name']:<8} {row['subnet']:<18} wildcard {row['wildcard']}")
    print("summary route:", summarize.single_summary([r["subnet"] for r in plan]))
    print("OSPF uplink costs (ref 100G):",
          ", ".join(f"{rate}={cost}" for rate, cost in uplink_costs()))


if __name__ == "__main__":
    main()
