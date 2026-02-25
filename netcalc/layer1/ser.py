"""Symbol error rate (SER) for PAM-M and square QAM-M in Gaussian noise.

Modern links carry more than one bit per symbol: 50G/100G-per-lane Ethernet
uses PAM4, coherent optics use QPSK/16QAM. These closed-form AWGN
expressions relate the signal-to-noise ratio per symbol (Es/N0, written as
"SNR" here) to the symbol error rate, and Gray coding lets us approximate
the bit error rate as ``SER / log2(M)``.

Usage::

    python -m netcalc.layer1.ser pam --levels 4 --snr-db 20
    python -m netcalc.layer1.ser qam --order 16 --snr-db 18
    python -m netcalc.layer1.ser ebn0 --ebn0-db 10 --bits 2
"""

import argparse
import math


def q_function(x):
    """Gaussian tail probability Q(x) = P(N(0,1) > x)."""
    return 0.5 * math.erfc(x / math.sqrt(2))


def pam_ser(levels, snr_db):
    """SER of M-level PAM at average SNR per symbol ``snr_db``.

    ``SER = 2 (1 - 1/M) Q( sqrt(3 SNR / (M^2 - 1)) )``
    """
    snr = 10 ** (snr_db / 10)
    return 2 * (1 - 1 / levels) * q_function(math.sqrt(3 * snr / (levels ** 2 - 1)))


def qam_ser(order, snr_db):
    """SER of square M-QAM: two independent sqrt(M)-PAM rails.

    ``SER = 1 - (1 - 2 (1 - 1/sqrt(M)) Q( sqrt(3 SNR / (M - 1)) ))^2``
    """
    root = math.isqrt(order)
    if root * root != order:
        raise ValueError("only square QAM orders (4, 16, 64, ...) are supported")
    snr = 10 ** (snr_db / 10)
    rail = 2 * (1 - 1 / root) * q_function(math.sqrt(3 * snr / (order - 1)))
    return 1 - (1 - rail) ** 2


def ser_to_ber(ser, bits_per_symbol):
    """Gray-coded approximation: one bit wrong per symbol error."""
    return ser / bits_per_symbol


def ebn0_to_snr_db(ebn0_db, bits_per_symbol):
    """Convert Eb/N0 to Es/N0: ``Es/N0 = Eb/N0 + 10 log10(bits per symbol)``."""
    return ebn0_db + 10 * math.log10(bits_per_symbol)
