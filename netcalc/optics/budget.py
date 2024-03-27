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


def max_reach_km(tx_dbm, sensitivity_dbm, alpha_db_km=0.25, connectors=2, splice_every_km=0.0,
                 safety_db=3.0, connector_db=CONNECTOR_LOSS_DB, splice_db=SPLICE_LOSS_DB):
    """Attenuation-limited reach (km).

    With a splice every ``splice_every_km`` the effective loss per km becomes
    ``alpha + splice_db / splice_every_km``.
    """
    per_km = alpha_db_km + (splice_db / splice_every_km if splice_every_km else 0.0)
    available = power_budget(tx_dbm, sensitivity_dbm) - safety_db - connectors * connector_db
    return max(available, 0.0) / per_km


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    def span_args(p):
        p.add_argument("--km", type=float, required=True)
        p.add_argument("--alpha", type=float, default=0.25, help="fibre loss in dB/km")
        p.add_argument("--connectors", type=int, default=2)
        p.add_argument("--splices", type=int, default=0)

    span_args(sub.add_parser("loss", help="passive loss of a span"))
    p = sub.add_parser("margin", help="power margin of a link")
    span_args(p)
    p.add_argument("--tx", type=float, required=True, help="launch power in dBm")
    p.add_argument("--sens", type=float, required=True, help="receiver sensitivity in dBm")
    p.add_argument("--max-rx", type=float, default=None, help="receiver overload in dBm")
    p.add_argument("--safety", type=float, default=3.0, help="safety margin in dB")
    p = sub.add_parser("reach", help="attenuation-limited reach")
    p.add_argument("--tx", type=float, required=True)
    p.add_argument("--sens", type=float, required=True)
    p.add_argument("--alpha", type=float, default=0.25)
    p.add_argument("--connectors", type=int, default=2)
    p.add_argument("--splice-every", type=float, default=0.0, help="km between splices")
    p.add_argument("--safety", type=float, default=3.0)
    args = parser.parse_args(argv)

    if args.cmd == "loss":
        print(f"span loss = {span_loss(args.km, args.alpha, args.connectors, args.splices):.2f} dB")
    elif args.cmd == "margin":
        loss = span_loss(args.km, args.alpha, args.connectors, args.splices)
        rx = received_power(args.tx, loss)
        margin = link_margin(args.tx, args.sens, loss, args.safety)
        verdict = "PASS" if margin >= 0 else "FAIL"
        print(f"loss {loss:.2f} dB, rx {rx:.2f} dBm ({dbm_to_mw(rx) * 1000:.1f} uW), "
              f"margin {margin:.2f} dB -> {verdict}")
        if args.max_rx is not None:
            ok, atten = overload_check(args.tx, loss, args.max_rx)
            print("receiver not overloaded" if ok else f"overload: add a {atten:.1f} dB attenuator")
    else:
        km = max_reach_km(args.tx, args.sens, args.alpha, args.connectors, args.splice_every,
                          args.safety)
        print(f"attenuation-limited reach = {km:.1f} km")


if __name__ == "__main__":
    main()
