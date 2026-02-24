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
