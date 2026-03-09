"""Optical signal-to-noise ratio (OSNR) and electrical SNR.

OSNR is measured on an optical spectrum analyser as signal power over ASE
noise power in a 0.1 nm reference bandwidth (12.5 GHz at 1550 nm). Coherent
DSPs report electrical SNR in the symbol bandwidth instead. They are related
by::

    OSNR = (p * Rs / (2 * Bref)) * SNR

where ``p`` is the number of polarisations (2 for dual-pol), ``Rs`` the
symbol rate and ``Bref`` the reference bandwidth in Hz.

For an amplified line the rule of thumb per EDFA is::

    OSNR_dB = 58 + P_in_dBm - NF_dB          (0.1 nm reference)

and noise from cascaded sections adds in linear 1/OSNR.

Usage::

    python -m netcalc.layer1.osnr to-snr --osnr-db 20 --baud 64
    python -m netcalc.layer1.osnr chain --launch-dbm 1 --span-loss 22 --nf 5.5 --spans 10
    python -m netcalc.layer1.osnr cascade 25 28 30
"""

import argparse
import math

from netcalc.units import SPEED_OF_LIGHT_M_S


def ref_bandwidth_hz(ref_nm=0.1, wavelength_nm=1550.0):
    """Optical reference bandwidth in Hz: ``c * dlambda / lambda^2``."""
    return SPEED_OF_LIGHT_M_S * (ref_nm * 1e-9) / (wavelength_nm * 1e-9) ** 2


def osnr_to_snr_db(osnr_db, baud_g, polarizations=2, ref_nm=0.1, wavelength_nm=1550.0):
    """Electrical SNR (dB) from OSNR (dB) for a signal at ``baud_g`` GBd."""
    bref = ref_bandwidth_hz(ref_nm, wavelength_nm)
    return osnr_db - 10 * math.log10(polarizations * baud_g * 1e9 / (2 * bref))


def snr_to_osnr_db(snr_db, baud_g, polarizations=2, ref_nm=0.1, wavelength_nm=1550.0):
    """Required OSNR (dB) to deliver an electrical SNR (dB)."""
    bref = ref_bandwidth_hz(ref_nm, wavelength_nm)
    return snr_db + 10 * math.log10(polarizations * baud_g * 1e9 / (2 * bref))


def osnr_from_powers(signal_dbm, noise_dbm, noise_bw_nm, ref_nm=0.1):
    """OSNR from measured signal and noise powers, normalised to ``ref_nm``."""
    return signal_dbm - (noise_dbm + 10 * math.log10(ref_nm / noise_bw_nm))


def cascade_osnr_db(*osnr_db):
    """Total OSNR of independent noise contributions: 1/OSNR adds linearly."""
    inv = sum(10 ** (-x / 10) for x in osnr_db)
    return -10 * math.log10(inv)
