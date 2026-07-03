"""Size a RoCE/Ultra Ethernet style backend fabric for one training job.

Answers in one run: how uneven ECMP is versus spraying for the job's flows,
the PFC headroom per port, the reorder buffer a multipath transport needs,
and how long one all-reduce takes.

    python examples/ai_fabric_sizing.py --gpus 512 --rate 400G --paths 64 --size 1GB
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netcalc.aifabric import collectives, loadbalance, mrc, roce  # noqa: E402
from netcalc.units import fmt_size, fmt_time, parse_rate, parse_size, parse_time  # noqa: E402
