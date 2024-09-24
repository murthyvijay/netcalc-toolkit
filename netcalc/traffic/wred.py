"""RED / WRED: average queue tracking and early-drop (or ECN-mark) probability.

Random Early Detection works on an exponentially weighted moving average of
the queue depth, so short bursts pass but standing queues are trimmed::

    avg = (1 - w) * avg + w * q            w = 2^-n (Cisco's exponential weight, n = 9)

The drop probability rises linearly from 0 at ``min_th`` to ``1/MPD`` at
``max_th`` (MPD = mark probability denominator) and is 1 above ``max_th``.
Floyd and Jacobson spread drops evenly by scaling with the number of packets
since the last drop: ``pa = pb / (1 - count * pb)``. Weighted RED keeps one
profile per drop precedence, with lower thresholds for traffic that should
go first (for example AFx3 before AFx2 before AFx1).

Usage::

    python -m netcalc.traffic.wred prob --avg 35 --min 20 --max 40 --mpd 10
    python -m netcalc.traffic.wred ewma --n 9 0 50 50 50 50
    python -m netcalc.traffic.wred profiles --limit 64
"""

import argparse
import math


def drop_probability(avg, min_th, max_th, mpd=10):
    """Early-drop probability for an average queue depth.

    >>> drop_probability(30, 20, 40, mpd=10)
    0.05
    """
    if avg < min_th:
        return 0.0
    if avg >= max_th:
        return 1.0
    return (avg - min_th) / (max_th - min_th) / mpd


def spaced_probability(pb, count):
    """Floyd-Jacobson probability after ``count`` packets accepted since the last drop."""
    if count * pb >= 1:
        return 1.0
    return pb / (1 - count * pb)


def ewma_weight(n):
    """EWMA weight ``2^-n`` for an exponential weighting constant ``n``."""
    return 2.0 ** -n


def ewma_series(samples, n=9, start=0.0):
    """Average queue depth after each instantaneous sample."""
    w = ewma_weight(n)
    avg = start
    out = []
    for q in samples:
        avg = (1 - w) * avg + w * q
        out.append(avg)
    return out


def samples_to_reach(fraction, n=9):
    """Samples of a step change before the average reaches ``fraction`` of it."""
    return math.ceil(math.log(1 - fraction) / math.log(1 - ewma_weight(n)))


def af_profiles(queue_limit, mpd=10):
    """Example WRED profiles per AF drop precedence: ``{1: (min, max, mpd), ...}``.

    AFx1 starts dropping at 75 % of the queue limit, AFx2 at 50 % and AFx3 at
    25 %; all reach their maximum probability at the limit.
    """
    return {dp: (queue_limit * start, queue_limit, mpd)
            for dp, start in ((1, 0.75), (2, 0.5), (3, 0.25))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prob", help="drop probability at an average depth")
    p.add_argument("--avg", type=float, required=True)
    p.add_argument("--min", type=float, required=True)
    p.add_argument("--max", type=float, required=True)
    p.add_argument("--mpd", type=float, default=10)
    p = sub.add_parser("ewma", help="average queue for a series of samples")
    p.add_argument("--n", type=int, default=9, help="exponential weighting constant")
    p.add_argument("samples", type=float, nargs="+")
    p = sub.add_parser("profiles", help="example WRED profiles per AF drop precedence")
    p.add_argument("--limit", type=float, required=True, help="queue limit in packets")
    p.add_argument("--mpd", type=float, default=10)
    args = parser.parse_args(argv)

    if args.cmd == "prob":
        print(f"drop probability = {drop_probability(args.avg, args.min, args.max, args.mpd):.4f}")
    elif args.cmd == "ewma":
        for q, avg in zip(args.samples, ewma_series(args.samples, args.n)):
            print(f"q={q:<8g} avg={avg:.4f}")
        print(f"a step reaches 63 % of its size after {samples_to_reach(0.63, args.n)} samples")
    else:
        for dp, (lo, hi, mpd) in af_profiles(args.limit, args.mpd).items():
            print(f"AFx{dp}: min {lo:g}, max {hi:g}, 1/{mpd:g} at max")


if __name__ == "__main__":
    main()
