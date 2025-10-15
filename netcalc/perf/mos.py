"""Voice quality: E-model R-factor and MOS from delay, jitter and loss.

The ITU-T G.107 E-model rates a call on a 0-100 scale::

    R = 93.2 - Id - Ie_eff

``Id`` is the delay impairment, approximated (Cole and Rosenbluth) as
``0.024 d + 0.11 (d - 177.3) H(d - 177.3)`` for one-way mouth-to-ear delay
d in ms, where H is the step function. A jitter buffer turns jitter into
delay, commonly sized at twice the jitter. ``Ie_eff`` is the equipment
impairment of the codec under random loss::

    Ie_eff = Ie + (95 - Ie) * Ppl / (Ppl + Bpl)

(G.711: Ie = 0, Bpl = 25.1 with PLC; G.729A: Ie = 11, Bpl = 19). R maps to a
mean opinion score by ``MOS = 1 + 0.035 R + 7e-6 R (R - 60)(100 - R)``;
R 80 (MOS ~4.0) is "satisfied", below 60 (MOS ~3.1) many users complain.

Usage::

    python -m netcalc.perf.mos score --delay 80ms --jitter 10ms --loss 0.5 --codec g711
    python -m netcalc.perf.mos budget --codec g729 --target-mos 3.6 --loss 1
"""

import argparse

from netcalc.units import parse_time

CODECS = {"g711": (0.0, 25.1), "g729": (11.0, 19.0), "g722": (0.0, 25.1), "opus": (0.0, 30.0)}


def delay_impairment(one_way_ms):
    """Id: delay impairment for a one-way mouth-to-ear delay in ms."""
    excess = max(one_way_ms - 177.3, 0.0)
    return 0.024 * one_way_ms + 0.11 * excess


def loss_impairment(loss_pct, codec="g711"):
    """Ie_eff: codec impairment under ``loss_pct`` percent random packet loss."""
    ie, bpl = CODECS[codec]
    return ie + (95 - ie) * loss_pct / (loss_pct + bpl)
