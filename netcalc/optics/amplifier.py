"""Optical amplifier planning: spans, gain, per-channel power and cascaded noise figure.

* An EDFA with a fixed total output power shares it between channels::

      P_channel = P_total - 10 * log10(N)          (dBm)

  so adding channels to a live system lowers per-channel power unless the
  amplifier runs in constant-gain mode.
* Each inline amplifier's gain makes up the preceding span loss (plus any
  ROADM or compensator loss in that span).
* Noise figures of cascaded stages combine with the Friis formula, in
  linear units::

      F = F1 + (F2 - 1) / G1 + (F3 - 1) / (G1 * G2) + ...

  which is why a low-noise first stage matters most.

Usage::

    python -m netcalc.optics.amplifier channel --total 20 --channels 40
    python -m netcalc.optics.amplifier spans --km 600 --max-span 80
    python -m netcalc.optics.amplifier friis 20:5 15:6 10:8
"""

import argparse
import math

from netcalc.units import db_to_linear, linear_to_db


def per_channel_power(total_dbm, channels):
    """Per-channel power (dBm) when ``channels`` share ``total_dbm``.

    >>> round(per_channel_power(20, 40), 2)
    3.98
    """
    return total_dbm - 10 * math.log10(channels)


def total_power(channel_dbm, channels):
    """Total composite power (dBm) of ``channels`` at ``channel_dbm`` each."""
    return channel_dbm + 10 * math.log10(channels)


def spans_needed(km, max_span_km):
    """Number of spans to cover ``km`` with spans no longer than ``max_span_km``."""
    return max(1, math.ceil(round(km / max_span_km, 9)))


def inline_amplifiers(km, max_span_km):
    """Inline amplifiers needed between the terminal booster and pre-amplifier."""
    return spans_needed(km, max_span_km) - 1


def gain_needed(span_loss_db, extra_loss_db=0.0):
    """Amplifier gain (dB) that restores the launch power after a span."""
    return span_loss_db + extra_loss_db
