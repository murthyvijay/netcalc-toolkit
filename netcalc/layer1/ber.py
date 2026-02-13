"""Bit error ratio (BER) measurement and test-time planning.

BER is the number of errored bits divided by the number of bits received.
Because errors are rare, the useful questions in the lab are statistical:

* How many bits must I send, error free, to claim BER < 1e-12 with 95 %
  confidence?
* Given what I actually measured, what confidence do I have?
* How long will that take at 100 Gb/s?

Errors are modelled as a Poisson process, which is the standard assumption
behind the confidence-level tables used by BERT vendors.

Usage::

    python -m netcalc.layer1.ber measure --errors 3 --bits 1e12
    python -m netcalc.layer1.ber bits --target 1e-12 --confidence 0.95
    python -m netcalc.layer1.ber time --target 1e-12 --rate 100G --errors 1
"""

import argparse
import math

from netcalc.units import fmt_time, parse_rate


def ber(errors, bits):
    """Return the measured bit error ratio ``errors / bits``.

    >>> ber(5, 1e12)
    5e-12
    """
    if bits <= 0:
        raise ValueError("bits must be positive")
    if errors < 0:
        raise ValueError("errors cannot be negative")
    return errors / bits


def poisson_cdf(k, mean):
    """Probability of observing ``k`` or fewer events when ``mean`` are expected."""
    term = math.exp(-mean)
    total = term
    for i in range(1, k + 1):
        term *= mean / i
        total += term
    return total


def confidence_level(bits, target_ber, errors=0):
    """Confidence that the true BER is below ``target_ber``.

    If the true BER were exactly ``target_ber`` we would expect
    ``bits * target_ber`` errors. The confidence level is the probability
    that such a link would have shown *more* errors than we observed.

    >>> round(confidence_level(3e12, 1e-12), 3)
    0.95
    """
    return 1.0 - poisson_cdf(errors, bits * target_ber)


def bits_for_confidence(target_ber, confidence=0.95, errors=0):
    """Number of bits needed to claim BER < ``target_ber`` at ``confidence``.

    With zero errors this is the closed form ``-ln(1 - CL) / BER`` (about
    3 / BER for 95 %). With ``errors`` allowed the Poisson tail is solved
    numerically.

    >>> round(bits_for_confidence(1e-12, 0.95) / 1e12, 3)
    2.996
    """
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    if errors == 0:
        return -math.log(1 - confidence) / target_ber
    lo, hi = 0.0, 1.0
    while poisson_cdf(errors, hi) > 1 - confidence:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if poisson_cdf(errors, mid) > 1 - confidence:
            lo = mid
        else:
            hi = mid
    return hi / target_ber
