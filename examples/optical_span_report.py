"""Plan an amplified DWDM route: spans, power, OSNR, dispersion and capacity.

Combines the optics tools: amplifier span planning and per-channel power,
the Layer 1 OSNR chain, chromatic-dispersion accumulation against a coherent
DSP tolerance, and the channel count and capacity of the C band.

    python examples/optical_span_report.py --km 600 --channels 64 --baud 64 --mod 16qam
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netcalc.layer1 import osnr  # noqa: E402
from netcalc.optics import amplifier, coherent, dispersion, dwdm  # noqa: E402
