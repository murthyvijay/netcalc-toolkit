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


def friis_nf_db(stages):
    """Cascaded noise figure (dB) of ``[(gain_db, nf_db), ...]`` in signal order.

    >>> round(friis_nf_db([(20, 5), (20, 5)]), 3)
    5.03
    """
    total_f = 0.0
    gain = 1.0
    for i, (g_db, nf_db) in enumerate(stages):
        f = db_to_linear(nf_db)
        total_f += f if i == 0 else (f - 1) / gain
        gain *= db_to_linear(g_db)
    return linear_to_db(total_f)


def parse_stages(items):
    """Parse ``["20:5", "15:6"]`` into ``[(20.0, 5.0), (15.0, 6.0)]``."""
    return [tuple(float(x) for x in item.split(":", 1)) for item in items]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("channel", help="per-channel power from total output")
    p.add_argument("--total", type=float, required=True, help="total output in dBm")
    p.add_argument("--channels", type=int, required=True)
    p = sub.add_parser("spans", help="spans and amplifiers for a route")
    p.add_argument("--km", type=float, required=True)
    p.add_argument("--max-span", type=float, default=80.0)
    p.add_argument("--alpha", type=float, default=0.25, help="dB/km, to estimate gain")
    p = sub.add_parser("friis", help="cascaded noise figure")
    p.add_argument("stages", nargs="+", help="gain_dB:NF_dB per stage, in order")
    args = parser.parse_args(argv)

    if args.cmd == "channel":
        print(f"{per_channel_power(args.total, args.channels):.2f} dBm per channel")
    elif args.cmd == "spans":
        n = spans_needed(args.km, args.max_span)
        span_km = args.km / n
        print(f"{n} spans of {span_km:.1f} km, {inline_amplifiers(args.km, args.max_span)} inline "
              f"amplifiers, ~{gain_needed(span_km * args.alpha):.1f} dB gain each")
    else:
        print(f"cascaded NF = {friis_nf_db(parse_stages(args.stages)):.2f} dB")


if __name__ == "__main__":
    main()
