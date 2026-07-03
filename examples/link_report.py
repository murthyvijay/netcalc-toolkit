"""Print a one-page health report for a PAM4 link from its pre-FEC BER.

Combines the Layer 1 tools: Q-factor, KP4 post-FEC BER, FEC margin and how
long a BER test would need to run to confirm the post-FEC figure.

    python examples/link_report.py --pre-ber 3e-7 --rate 400G
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netcalc.layer1 import ber, fec, qfactor  # noqa: E402
from netcalc.units import fmt_time, parse_rate  # noqa: E402


def link_report(pre_ber, rate_bps, code="kp4", target=1e-13):
    """Return the report lines for a link."""
    margin = fec.fec_margin(pre_ber, code, target)
    q = qfactor.ber_to_q(pre_ber)
    return [
        f"pre-FEC BER        {pre_ber:.2e}  (Q = {qfactor.q_to_db(q):.2f} dB)",
        f"post-FEC BER       {margin['post_fec_ber']:.2e}",
        f"FEC threshold      {margin['threshold']:.2e}",
        f"FEC margin         {margin['decades']:.2f} decades, {margin['q_margin_db']:.2f} dB Q",
        f"verdict            {'PASS' if margin['pass'] else 'FAIL'}",
        f"time to verify pre-FEC BER at 95 %: "
        f"{fmt_time(ber.required_test_time(pre_ber, rate_bps))}",
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pre-ber", type=float, required=True)
    parser.add_argument("--rate", default="400G")
    parser.add_argument("--code", default="kp4")
    args = parser.parse_args()
    print("\n".join(link_report(args.pre_ber, parse_rate(args.rate), args.code)))


if __name__ == "__main__":
    main()
