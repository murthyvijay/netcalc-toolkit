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
