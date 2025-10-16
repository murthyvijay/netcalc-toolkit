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


def effective_delay_ms(one_way_ms, jitter_ms, buffer_factor=2.0, codec_delay_ms=0.0):
    """Mouth-to-ear delay including the jitter buffer and codec delay."""
    return one_way_ms + buffer_factor * jitter_ms + codec_delay_ms


def r_factor(one_way_ms, jitter_ms=0.0, loss_pct=0.0, codec="g711"):
    """E-model R-factor (0..100)."""
    d = effective_delay_ms(one_way_ms, jitter_ms)
    return max(0.0, min(100.0, 93.2 - delay_impairment(d) - loss_impairment(loss_pct, codec)))


def r_to_mos(r):
    """Mean opinion score (1..4.5) for an R-factor.

    >>> round(r_to_mos(93.2), 2)
    4.41
    """
    if r <= 0:
        return 1.0
    if r >= 100:
        return 4.5
    return 1 + 0.035 * r + 7e-6 * r * (r - 60) * (100 - r)


def max_delay_for_mos(target_mos, loss_pct=0.0, codec="g711"):
    """Largest one-way delay (ms, jitter included) that still reaches ``target_mos``."""
    lo, hi = 0.0, 1000.0
    if r_to_mos(r_factor(0, 0, loss_pct, codec)) < target_mos:
        return 0.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if r_to_mos(r_factor(mid, 0, loss_pct, codec)) >= target_mos:
            lo = mid
        else:
            hi = mid
    return lo


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("score", help="R-factor and MOS for measured conditions")
    p.add_argument("--delay", required=True, help="one-way network delay")
    p.add_argument("--jitter", default="0ms")
    p.add_argument("--loss", type=float, default=0.0, help="percent")
    p.add_argument("--codec", choices=sorted(CODECS), default="g711")
    p = sub.add_parser("budget", help="delay budget for a target MOS")
    p.add_argument("--target-mos", type=float, default=4.0)
    p.add_argument("--loss", type=float, default=0.0)
    p.add_argument("--codec", choices=sorted(CODECS), default="g711")
    args = parser.parse_args(argv)

    if args.cmd == "score":
        r = r_factor(parse_time(args.delay) * 1e3, parse_time(args.jitter) * 1e3, args.loss, args.codec)
        print(f"R = {r:.1f}, MOS = {r_to_mos(r):.2f}")
    else:
        d = max_delay_for_mos(args.target_mos, args.loss, args.codec)
        print(f"MOS {args.target_mos:g} with {args.codec} at {args.loss:g} % loss allows "
              f"{d:.0f} ms one-way (including jitter buffer)")


if __name__ == "__main__":
    main()
