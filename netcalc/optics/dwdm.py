"""DWDM channel plans on the ITU-T G.694.1 frequency grid.

The fixed grid anchors every channel to 193.1 THz::

    f(n) = 193.1 THz + n * spacing          (spacing 12.5, 25, 50 or 100 GHz)

and the wavelength follows from ``lambda = c / f``. The flexible grid
(flexgrid) puts a slot's centre at ``193.1 THz + n * 6.25 GHz`` and gives it
a width of ``m * 12.5 GHz``, so a 64 GBd carrier can sit in a 75 GHz slot
instead of wasting a 100 GHz channel. Common bands: C band 191.3-196.1 THz
(about 1529-1567 nm), L band 186.0-190.8 THz (about 1571-1612 nm).

Usage::

    python -m netcalc.optics.dwdm channel --n -10 --spacing 50
    python -m netcalc.optics.dwdm convert 1550.12nm
    python -m netcalc.optics.dwdm plan --band C --spacing 100
    python -m netcalc.optics.dwdm flex --baud 64 --rolloff 0.1
"""

import argparse
import math

from netcalc.units import SPEED_OF_LIGHT_M_S

ANCHOR_THZ = 193.1
FLEX_CENTRE_GHZ = 6.25
FLEX_WIDTH_GHZ = 12.5
BANDS_THZ = {"C": (191.3, 196.1), "L": (186.0, 190.8)}


def frequency_thz(n, spacing_ghz=50.0):
    """Centre frequency (THz) of grid channel ``n`` at ``spacing_ghz``.

    >>> round(frequency_thz(-10, 50), 4)
    192.6
    """
    return ANCHOR_THZ + n * spacing_ghz / 1000.0


def thz_to_nm(freq_thz):
    """Vacuum wavelength (nm) of an optical frequency (THz).

    >>> round(thz_to_nm(193.1), 2)
    1552.52
    """
    return SPEED_OF_LIGHT_M_S / (freq_thz * 1e12) * 1e9


def nm_to_thz(wavelength_nm):
    """Optical frequency (THz) of a vacuum wavelength (nm)."""
    return SPEED_OF_LIGHT_M_S / (wavelength_nm * 1e-9) / 1e12


def channel_number(freq_thz, spacing_ghz=50.0):
    """Nearest grid index ``n`` and the offset (GHz) of ``freq_thz`` from it."""
    n = round((freq_thz - ANCHOR_THZ) * 1000.0 / spacing_ghz)
    return n, (freq_thz - frequency_thz(n, spacing_ghz)) * 1000.0


def nm_spacing(spacing_ghz, wavelength_nm=1550.0):
    """Channel spacing in nm: ``dlambda = lambda^2 * df / c`` (0.8 nm for 100 GHz)."""
    return (wavelength_nm * 1e-9) ** 2 * spacing_ghz * 1e9 / SPEED_OF_LIGHT_M_S * 1e9


def band_plan(band="C", spacing_ghz=100.0):
    """Every grid channel inside ``band`` as ``(n, THz, nm)`` tuples, low to high."""
    lo, hi = BANDS_THZ[band.upper()]
    step = spacing_ghz / 1000.0
    first = math.ceil(round((lo - ANCHOR_THZ) / step, 6))
    last = math.floor(round((hi - ANCHOR_THZ) / step, 6))
    plan = []
    for n in range(first, last + 1):
        f = frequency_thz(n, spacing_ghz)
        plan.append((n, f, thz_to_nm(f)))
    return plan


def flex_slot(baud_g, rolloff=0.1, guard_ghz=0.0):
    """Smallest flexgrid slot for a carrier: returns ``(m, width_ghz)``.

    Occupied bandwidth is ``baud * (1 + rolloff) + guard``; the slot width is
    that rounded up to a multiple of 12.5 GHz.

    >>> flex_slot(64, 0.1)
    (6, 75.0)
    """
    occupied = baud_g * (1 + rolloff) + guard_ghz
    m = math.ceil(round(occupied / FLEX_WIDTH_GHZ, 9))
    return m, m * FLEX_WIDTH_GHZ
