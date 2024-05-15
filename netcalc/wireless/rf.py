"""RF link budget: free-space path loss, EIRP, Fresnel clearance and radio horizon.

* **Free-space path loss** with distance in km and frequency in MHz::

      FSPL_dB = 20 log10(d_km) + 20 log10(f_MHz) + 32.44

* **EIRP** = transmitter power - cable loss + antenna gain (dBm, dBi).
  Antenna gain quoted in dBd is relative to a dipole: ``dBi = dBd + 2.15``.
* **Received power** = EIRP - FSPL - other losses + receive antenna gain;
  the fade margin is received power minus receiver sensitivity.
* **Fresnel zone**: the radius of the n-th zone at a point d1 km from one
  end and d2 km from the other is ``17.32 * sqrt(n d1 d2 / (f_GHz (d1 + d2)))``
  metres. Point-to-point links keep at least 60 % of zone 1 clear.
* **Earth bulge and radio horizon** use an effective earth radius factor
  ``k`` (4/3 for a standard atmosphere): bulge ``= d1 d2 / (12.74 k)`` m and
  horizon ``= 3.57 sqrt(k h)`` km for an antenna ``h`` metres high.

Usage::

    python -m netcalc.wireless.rf fspl --km 10 --mhz 5800
    python -m netcalc.wireless.rf link --tx 20 --tx-gain 23 --rx-gain 23 --km 10 --mhz 5800 --sens -75
    python -m netcalc.wireless.rf fresnel --km 10 --ghz 5.8
    python -m netcalc.wireless.rf horizon --height 30
"""

import argparse
import math

DIPOLE_GAIN_DBI = 2.15
STANDARD_K = 4.0 / 3.0


def fspl_db(km, mhz):
    """Free-space path loss (dB).

    >>> round(fspl_db(1, 2400), 2)
    100.04
    """
    return 20 * math.log10(km) + 20 * math.log10(mhz) + 32.44


def eirp_dbm(tx_dbm, antenna_dbi, cable_loss_db=0.0):
    """Effective isotropic radiated power (dBm)."""
    return tx_dbm - cable_loss_db + antenna_dbi


def dbd_to_dbi(dbd):
    """Convert antenna gain relative to a dipole into dBi."""
    return dbd + DIPOLE_GAIN_DBI
