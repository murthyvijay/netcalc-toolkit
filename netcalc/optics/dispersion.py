"""Chromatic dispersion and PMD limits for direct-detect and coherent links.

* **Chromatic dispersion (CD)**: different wavelengths travel at different
  speeds, so a pulse spreads by ``dt = D * L * dlambda``. Accumulated CD is
  ``D * L`` ps/nm, with ``D`` about 17 ps/(nm km) for G.652 fibre at
  1550 nm and near zero at 1310 nm. A direct-detect signal tolerates roughly
  one bit period of spreading; with the modulated spectral width
  ``dlambda = lambda^2 * B / c`` that gives::

      L_max = c / (D * lambda^2 * B^2)

  about 73 km at 10 Gb/s and under 1 km at 100 Gb/s per lane, which is why
  long 1550 nm links either use dispersion compensation or coherent DSPs
  that undo CD electronically up to a stated tolerance.
* **Polarisation mode dispersion (PMD)**: the mean differential group delay
  grows with the square root of length, ``DGD = PMD_coef * sqrt(L)``.
  Direct-detect NRZ needs the mean DGD below about 10 % of the bit period.

Usage::

    python -m netcalc.optics.dispersion cd --km 80
    python -m netcalc.optics.dispersion reach --rate 10G
    python -m netcalc.optics.dispersion pmd --km 600 --coef 0.1 --rate 10G
"""

import argparse

from netcalc.units import SPEED_OF_LIGHT_M_S, parse_rate

SMF_D_PS_NM_KM = 17.0
PMD_COEF_PS_SQRT_KM = 0.1


def accumulated_cd(km, d_ps_nm_km=SMF_D_PS_NM_KM):
    """Accumulated chromatic dispersion (ps/nm) over ``km`` of fibre."""
    return d_ps_nm_km * km


def signal_width_nm(bitrate_bps, wavelength_nm=1550.0):
    """Spectral width (nm) of a signal modulated at ``bitrate_bps``: ``lambda^2 B / c``."""
    return (wavelength_nm * 1e-9) ** 2 * bitrate_bps / SPEED_OF_LIGHT_M_S * 1e9


def pulse_spread_ps(km, bitrate_bps, d_ps_nm_km=SMF_D_PS_NM_KM, wavelength_nm=1550.0):
    """Pulse spreading (ps) caused by CD for a signal at ``bitrate_bps``."""
    return abs(accumulated_cd(km, d_ps_nm_km)) * signal_width_nm(bitrate_bps, wavelength_nm)
