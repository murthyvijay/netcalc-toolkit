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
