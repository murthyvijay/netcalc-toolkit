"""Policer colour marking: single-rate (RFC 2697) and two-rate (RFC 2698) three-colour markers.

* **srTCM** (CIR, CBS, EBS): two token buckets that start full. Tokens
  arrive at CIR and fill the committed bucket first; the overflow fills the
  excess bucket. A packet of B bytes is green if the committed bucket holds
  B tokens, otherwise yellow if the excess bucket does, otherwise red.
* **trTCM** (CIR, CBS, PIR, PBS): a peak bucket filled at PIR and a
  committed bucket filled at CIR. A packet is red if it exceeds the peak
  bucket, yellow if it fits the peak but not the committed bucket, and green
  if it fits both.

Both markers here are colour-blind and take a trace of
``(arrival_time_s, bytes)`` packets.

Usage::

    python -m netcalc.traffic.marker srtcm --cir 1M --cbs 3000 --ebs 3000 0:1500 0:1500 0:1500 0.01:1500
    python -m netcalc.traffic.marker trtcm --cir 1M --cbs 1500 --pir 2M --pbs 3000 0:1500 0:1500 0:1500
    python -m netcalc.traffic.marker burst --cir 10M --bc 15000 --window 10ms
"""

import argparse
from collections import Counter

from netcalc.units import parse_rate, parse_size, parse_time


def srtcm(packets, cir_bps, cbs_bytes, ebs_bytes):
    """Colour a packet trace with the RFC 2697 single-rate three-colour marker.

    >>> srtcm([(0, 1500)] * 3, 1e6, 1500, 1500)
    ['green', 'yellow', 'red']
    """
    tc, te = float(cbs_bytes), float(ebs_bytes)
    last = None
    colors = []
    for t, size in packets:
        if last is not None:
            tokens = (t - last) * cir_bps / 8
            room = cbs_bytes - tc
            tc += min(tokens, room)
            te = min(ebs_bytes, te + max(tokens - room, 0.0))
        last = t
        if tc >= size:
            tc -= size
            colors.append("green")
        elif te >= size:
            te -= size
            colors.append("yellow")
        else:
            colors.append("red")
    return colors


def trtcm(packets, cir_bps, cbs_bytes, pir_bps, pbs_bytes):
    """Colour a packet trace with the RFC 2698 two-rate three-colour marker."""
    if pir_bps < cir_bps:
        raise ValueError("PIR must be at least CIR")
    tc, tp = float(cbs_bytes), float(pbs_bytes)
    last = None
    colors = []
    for t, size in packets:
        if last is not None:
            tc = min(cbs_bytes, tc + (t - last) * cir_bps / 8)
            tp = min(pbs_bytes, tp + (t - last) * pir_bps / 8)
        last = t
        if tp < size:
            colors.append("red")
        elif tc < size:
            tp -= size
            colors.append("yellow")
        else:
            tp -= size
            tc -= size
            colors.append("green")
    return colors


def color_summary(packets, colors):
    """Bytes per colour: ``{"green": ..., "yellow": ..., "red": ...}``."""
    out = Counter({"green": 0, "yellow": 0, "red": 0})
    for (_, size), color in zip(packets, colors):
        out[color] += size
    return dict(out)


def conforming_bytes(cir_bps, bc_bytes, window_s):
    """Most bytes a token bucket lets through in ``window_s`` starting full."""
    return bc_bytes + cir_bps * window_s / 8
