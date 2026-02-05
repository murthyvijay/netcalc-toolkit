"""Q-factor <-> BER conversion for binary (NRZ) signalling.

For a binary signal with Gaussian noise the Q-factor is the eye opening
divided by the noise: ``Q = (mu1 - mu0) / (sigma1 + sigma0)``. It maps to BER
through the complementary error function::

    BER = 0.5 * erfc(Q / sqrt(2))

Q is often quoted in dB as ``20 * log10(Q)`` (an amplitude ratio).

Usage::

    python -m netcalc.layer1.qfactor to-ber 7
    python -m netcalc.layer1.qfactor to-q 1e-12
    python -m netcalc.layer1.qfactor eye --mu1 1.0 --mu0 0.0 --s1 0.07 --s0 0.06
"""

import argparse
import math


def q_to_ber(q):
    """BER of a binary signal with linear Q-factor ``q``.

    >>> f"{q_to_ber(7):.2e}"
    '1.28e-12'
    """
    return 0.5 * math.erfc(q / math.sqrt(2))


def ber_to_q(ber):
    """Linear Q-factor that gives ``ber`` (inverse of :func:`q_to_ber`).

    >>> round(ber_to_q(1e-12), 3)
    7.034
    """
    if not 0 < ber < 0.5:
        raise ValueError("BER must be between 0 and 0.5")
    lo, hi = 0.0, 40.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if q_to_ber(mid) > ber:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def q_to_db(q):
    """Express a linear Q-factor in dB (``20 * log10(q)``)."""
    return 20 * math.log10(q)


def db_to_q(q_db):
    """Convert a Q-factor in dB back to linear."""
    return 10 ** (q_db / 20)


def q_from_eye(mu1, mu0, sigma1, sigma0):
    """Q-factor from eye-diagram levels and their noise standard deviations."""
    return (mu1 - mu0) / (sigma1 + sigma0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("to-ber", help="Q (linear, or dB with --db) to BER")
    p.add_argument("q", type=float)
    p.add_argument("--db", action="store_true", help="Q is given in dB")
    p = sub.add_parser("to-q", help="BER to Q")
    p.add_argument("ber", type=float)
    p = sub.add_parser("eye", help="Q and BER from eye levels")
    for name in ("mu1", "mu0", "s1", "s0"):
        p.add_argument(f"--{name}", type=float, required=True)
    args = parser.parse_args(argv)

    if args.cmd == "to-ber":
        q = db_to_q(args.q) if args.db else args.q
        print(f"Q = {q:.3f} ({q_to_db(q):.2f} dB) -> BER = {q_to_ber(q):.3e}")
    elif args.cmd == "to-q":
        q = ber_to_q(args.ber)
        print(f"BER = {args.ber:.3e} -> Q = {q:.3f} ({q_to_db(q):.2f} dB)")
    else:
        q = q_from_eye(args.mu1, args.mu0, args.s1, args.s0)
        print(f"Q = {q:.3f} ({q_to_db(q):.2f} dB) -> BER = {q_to_ber(q):.3e}")


if __name__ == "__main__":
    main()
