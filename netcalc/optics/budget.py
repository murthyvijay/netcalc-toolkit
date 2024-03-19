"""Optical link power budget, loss budget and attenuation-limited reach.

The loss of a passive fibre span adds fibre, connector and splice losses::

    loss   = alpha * L + Nc * Lc + Ns * Ls
    margin = (P_tx - P_rx_sensitivity) - loss - safety_margin

Typical values: 0.35 dB/km at 1310 nm and 0.25 dB/km at 1550 nm for
single-mode fibre, 0.5 dB per mated connector pair (0.75 dB worst case in
TIA-568), 0.1 dB per fusion splice. A link can also fail because the
receiver is *overloaded*: short links with high-power optics need an
attenuator so the received power stays below the maximum input.

Usage::

    python -m netcalc.optics.budget loss --km 40 --alpha 0.25 --connectors 4 --splices 8
    python -m netcalc.optics.budget margin --km 40 --tx -1 --sens -18 --max-rx 0
    python -m netcalc.optics.budget reach --tx 2 --sens -20 --alpha 0.25
"""

import argparse

from netcalc.units import dbm_to_mw

FIBER_ATTENUATION_DB_KM = {"1310": 0.35, "1550": 0.25, "850-mmf": 3.0}
CONNECTOR_LOSS_DB = 0.5
SPLICE_LOSS_DB = 0.1


def span_loss(km, alpha_db_km=0.25, connectors=2, splices=0,
              connector_db=CONNECTOR_LOSS_DB, splice_db=SPLICE_LOSS_DB):
    """Total passive loss (dB) of a fibre span.

    >>> span_loss(40, 0.25, connectors=4, splices=8)
    12.8
    """
    return round(km * alpha_db_km + connectors * connector_db + splices * splice_db, 9)


def power_budget(tx_dbm, sensitivity_dbm):
    """Available power budget (dB): launch power minus receiver sensitivity."""
    return tx_dbm - sensitivity_dbm


def link_margin(tx_dbm, sensitivity_dbm, loss_db, safety_db=3.0):
    """Margin (dB) left after the span loss and a safety allowance; >= 0 passes."""
    return power_budget(tx_dbm, sensitivity_dbm) - loss_db - safety_db


def received_power(tx_dbm, loss_db):
    """Received optical power (dBm)."""
    return tx_dbm - loss_db


def overload_check(tx_dbm, loss_db, max_rx_dbm):
    """Return ``(ok, attenuation_db)`` against the receiver overload point.

    ``attenuation_db`` is the fixed attenuator needed to bring the received
    power down to ``max_rx_dbm`` (0 when the link is already fine).
    """
    excess = received_power(tx_dbm, loss_db) - max_rx_dbm
    return excess <= 0, max(excess, 0.0)
