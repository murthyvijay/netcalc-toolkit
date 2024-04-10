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


def cd_limited_reach_km(bitrate_bps, d_ps_nm_km=SMF_D_PS_NM_KM, wavelength_nm=1550.0):
    """Uncompensated reach (km) where CD spreading equals one bit period."""
    bit_period_ps = 1e12 / bitrate_bps
    return bit_period_ps / (abs(d_ps_nm_km) * signal_width_nm(bitrate_bps, wavelength_nm))


def compensation_needed(km, d_ps_nm_km=SMF_D_PS_NM_KM, tolerance_ps_nm=0.0):
    """Dispersion compensation (ps/nm, negative) that brings residual CD within tolerance."""
    excess = abs(accumulated_cd(km, d_ps_nm_km)) - tolerance_ps_nm
    return -max(excess, 0.0)


def mean_dgd_ps(km, coef_ps_sqrt_km=PMD_COEF_PS_SQRT_KM):
    """Mean differential group delay (ps) from PMD: ``coef * sqrt(L)``."""
    return coef_ps_sqrt_km * km ** 0.5


def pmd_limited_reach_km(bitrate_bps, coef_ps_sqrt_km=PMD_COEF_PS_SQRT_KM, fraction=0.1):
    """Reach (km) where the mean DGD reaches ``fraction`` of a bit period.

    >>> round(pmd_limited_reach_km(10e9))
    10000
    """
    bit_period_ps = 1e12 / bitrate_bps
    return (fraction * bit_period_ps / coef_ps_sqrt_km) ** 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("cd", help="accumulated chromatic dispersion")
    p.add_argument("--km", type=float, required=True)
    p.add_argument("--d", type=float, default=SMF_D_PS_NM_KM, help="ps/(nm km)")
    p.add_argument("--tolerance", type=float, default=0.0, help="receiver CD tolerance ps/nm")
    p = sub.add_parser("reach", help="CD- and PMD-limited reach of direct-detect NRZ")
    p.add_argument("--rate", required=True, help="bit rate per lane, e.g. 10G")
    p.add_argument("--d", type=float, default=SMF_D_PS_NM_KM)
    p.add_argument("--coef", type=float, default=PMD_COEF_PS_SQRT_KM, help="ps/sqrt(km)")
    p = sub.add_parser("pmd", help="mean DGD over a route")
    p.add_argument("--km", type=float, required=True)
    p.add_argument("--coef", type=float, default=PMD_COEF_PS_SQRT_KM)
    p.add_argument("--rate", default=None, help="bit rate to compare against")
    args = parser.parse_args(argv)

    if args.cmd == "cd":
        cd = accumulated_cd(args.km, args.d)
        print(f"accumulated CD = {cd:.0f} ps/nm")
        if args.tolerance:
            comp = compensation_needed(args.km, args.d, args.tolerance)
            print("within receiver tolerance" if comp == 0 else f"compensate {comp:.0f} ps/nm")
    elif args.cmd == "reach":
        rate = parse_rate(args.rate)
        print(f"CD-limited reach  = {cd_limited_reach_km(rate, args.d):.1f} km")
        print(f"PMD-limited reach = {pmd_limited_reach_km(rate, args.coef):.0f} km")
    else:
        dgd = mean_dgd_ps(args.km, args.coef)
        print(f"mean DGD = {dgd:.2f} ps")
        if args.rate:
            pct = dgd / (1e12 / parse_rate(args.rate)) * 100
            print(f"{pct:.1f} % of a bit period -> {'OK' if pct <= 10 else 'too high for NRZ'}")


if __name__ == "__main__":
    main()
