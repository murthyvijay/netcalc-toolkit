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
