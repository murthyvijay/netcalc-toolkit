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


def plan_route(km, max_span_km=80.0, alpha_db_km=0.22, amp_total_dbm=20.0, nf_db=5.5, channels=64):
    """Spans, per-span loss, launch power per channel and end-of-line OSNR."""
    spans = amplifier.spans_needed(km, max_span_km)
    span_km = km / spans
    span_loss = span_km * alpha_db_km
    launch = amplifier.per_channel_power(amp_total_dbm, channels)
    eol_osnr = osnr.amplifier_chain_osnr_db(launch, span_loss, nf_db, spans)
    return {"spans": spans, "span_km": span_km, "span_loss_db": span_loss,
            "launch_dbm": launch, "osnr_db": eol_osnr}
