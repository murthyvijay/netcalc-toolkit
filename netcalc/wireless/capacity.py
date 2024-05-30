"""Channel capacity, thermal noise floor and SINR.

* **Thermal noise** at room temperature is -174 dBm/Hz, so a receiver of
  bandwidth B and noise figure NF has the floor::

      N_dBm = -174 + 10 log10(B_Hz) + NF_dB

* **Shannon-Hartley**: no modulation can beat ``C = B log2(1 + SNR)``.
  Practical systems land a few dB short of it; the gap is a useful sanity
  check on any vendor data rate claim.
* **Eb/N0** relates to SNR by the ratio of bit rate to bandwidth:
  ``Eb/N0 = SNR - 10 log10(R / B)``.
* **SINR** adds interference powers to noise in linear units (mW) before
  taking the ratio.

Usage::

    python -m netcalc.wireless.capacity noise --bw 20M --nf 7
    python -m netcalc.wireless.capacity shannon --bw 80M --snr 30
    python -m netcalc.wireless.capacity snr --bw 20M --rate 100M
    python -m netcalc.wireless.capacity sinr --signal -60 --noise -95 --interferer -80 -85
"""

import argparse
import math

from netcalc.units import dbm_to_mw, fmt_rate, mw_to_dbm, parse_rate

THERMAL_NOISE_DBM_HZ = -174.0


def noise_floor_dbm(bandwidth_hz, nf_db=0.0):
    """Receiver noise floor (dBm) for a bandwidth and noise figure.

    >>> round(noise_floor_dbm(20e6), 1)
    -101.0
    """
    return THERMAL_NOISE_DBM_HZ + 10 * math.log10(bandwidth_hz) + nf_db


def shannon_capacity(bandwidth_hz, snr_db):
    """Shannon limit in bits per second."""
    return bandwidth_hz * math.log2(1 + 10 ** (snr_db / 10))


def spectral_efficiency(snr_db):
    """Shannon spectral efficiency in b/s/Hz."""
    return math.log2(1 + 10 ** (snr_db / 10))


def snr_for_rate_db(rate_bps, bandwidth_hz):
    """Minimum SNR (dB) at which ``rate_bps`` fits in ``bandwidth_hz``."""
    return 10 * math.log10(2 ** (rate_bps / bandwidth_hz) - 1)
