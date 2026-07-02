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
