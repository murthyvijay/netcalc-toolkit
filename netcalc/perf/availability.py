"""Availability: series and parallel systems, nines, downtime and MTBF/MTTR.

* Steady-state availability of a component is ``A = MTBF / (MTBF + MTTR)``.
* Components in **series** (all must work) multiply: ``A = A1 * A2 * ...``.
* Redundant components in **parallel** (any one is enough) fail together
  only if all fail: ``A = 1 - (1 - A1)(1 - A2)...``.
* **k-of-n** redundancy (at least k of n identical parts up) follows the
  binomial distribution.
* "Nines": 99.99 % is four nines, about 52.6 minutes of downtime a year.

Usage::

    python -m netcalc.perf.availability series 0.999 0.9995 0.9999
    python -m netcalc.perf.availability parallel 0.99 0.99
    python -m netcalc.perf.availability mtbf --mtbf 50000h --mttr 4h
    python -m netcalc.perf.availability nines 0.9999
"""

import argparse
import math

HOURS_PER_YEAR = 8766.0


def from_mtbf(mtbf, mttr):
    """Availability from mean time between failures and mean time to repair."""
    return mtbf / (mtbf + mttr)


def series(*availabilities):
    """Availability of components that must all work.

    >>> round(series(0.999, 0.999), 6)
    0.998001
    """
    return math.prod(availabilities)


def parallel(*availabilities):
    """Availability of redundant components where one is enough.

    >>> round(parallel(0.99, 0.99), 6)
    0.9999
    """
    return 1 - math.prod(1 - a for a in availabilities)


def k_of_n(k, n, availability):
    """Availability when at least ``k`` of ``n`` identical components must be up."""
    return sum(math.comb(n, i) * availability ** i * (1 - availability) ** (n - i)
               for i in range(k, n + 1))


def downtime_per_year(availability):
    """Expected downtime in minutes per year."""
    return (1 - availability) * HOURS_PER_YEAR * 60


def nines(availability):
    """Number of nines, e.g. 0.9995 -> 3.3."""
    return -math.log10(1 - availability)


def from_nines(n):
    """Availability from a number of nines (4 -> 0.9999)."""
    return 1 - 10 ** -n


def parse_hours(text):
    """Parse ``"50000h"``, ``"30d"`` or ``"45m"`` into hours."""
    text = str(text).strip().lower()
    scale = {"h": 1.0, "d": 24.0, "m": 1 / 60, "y": HOURS_PER_YEAR}
    if text[-1] in scale:
        return float(text[:-1]) * scale[text[-1]]
    return float(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("series", "parallel"):
        p = sub.add_parser(name, help=f"availability of components in {name}")
        p.add_argument("availability", type=float, nargs="+")
    p = sub.add_parser("kofn", help="at least k of n identical components")
    p.add_argument("--k", type=int, required=True)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--availability", type=float, required=True)
    p = sub.add_parser("mtbf", help="availability from MTBF and MTTR")
    p.add_argument("--mtbf", required=True, help="e.g. 50000h or 2y")
    p.add_argument("--mttr", required=True, help="e.g. 4h")
    p = sub.add_parser("nines", help="downtime for an availability")
    p.add_argument("availability", type=float)
    args = parser.parse_args(argv)

    if args.cmd == "series":
        a = series(*args.availability)
    elif args.cmd == "parallel":
        a = parallel(*args.availability)
    elif args.cmd == "kofn":
        a = k_of_n(args.k, args.n, args.availability)
    elif args.cmd == "mtbf":
        a = from_mtbf(parse_hours(args.mtbf), parse_hours(args.mttr))
    else:
        a = args.availability
    print(f"availability {a:.6%} ({nines(a):.2f} nines), "
          f"{downtime_per_year(a):.1f} min/year downtime")


if __name__ == "__main__":
    main()
