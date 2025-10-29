"""Size the back-end fabric and failure budget of a GPU training cluster.

Combines the AI fabric tools: leaf-spine sizing, data-parallel gradient
traffic, pipeline bubble, checkpoint size and the Young/Daly checkpoint
interval for the cluster's failure rate.

    python examples/ai_cluster_plan.py --gpus 2048 --radix 64 --params 70e9 --rate 400G
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netcalc.aifabric import checkpoint, parallelism, topology  # noqa: E402
from netcalc.units import fmt_size, fmt_time, parse_rate  # noqa: E402
