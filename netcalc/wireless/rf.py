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


def received_power_dbm(tx_dbm, tx_dbi, rx_dbi, km, mhz, losses_db=0.0):
    """Received signal level (dBm) over a free-space path."""
    return eirp_dbm(tx_dbm, tx_dbi) - fspl_db(km, mhz) - losses_db + rx_dbi


def fade_margin_db(rx_dbm, sensitivity_dbm):
    """Fade margin (dB): how far the received level sits above sensitivity."""
    return rx_dbm - sensitivity_dbm


def max_range_km(tx_dbm, tx_dbi, rx_dbi, mhz, sensitivity_dbm, margin_db=10.0, losses_db=0.0):
    """Longest free-space path (km) that still leaves ``margin_db`` of fade margin."""
    allowed_fspl = eirp_dbm(tx_dbm, tx_dbi) + rx_dbi - losses_db - sensitivity_dbm - margin_db
    return 10 ** ((allowed_fspl - 32.44 - 20 * math.log10(mhz)) / 20)


def fresnel_radius_m(d1_km, d2_km, ghz, zone=1):
    """Radius (m) of Fresnel zone ``zone`` at a point between the antennas."""
    return 17.32 * math.sqrt(zone * d1_km * d2_km / (ghz * (d1_km + d2_km)))


def earth_bulge_m(d1_km, d2_km, k=STANDARD_K):
    """Height (m) the earth's curvature rises at a point on the path."""
    return d1_km * d2_km / (12.74 * k)


def radio_horizon_km(height_m, k=STANDARD_K):
    """Distance (km) to the radio horizon from an antenna ``height_m`` high."""
    return 3.57 * math.sqrt(k * height_m)


def clearance_height_m(km, ghz, clear_fraction=0.6, k=STANDARD_K):
    """Mid-path clearance (m) above obstacles: earth bulge + ``clear_fraction`` of zone 1."""
    half = km / 2
    return earth_bulge_m(half, half, k) + clear_fraction * fresnel_radius_m(half, half, ghz)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("fspl", help="free-space path loss")
    p.add_argument("--km", type=float, required=True)
    p.add_argument("--mhz", type=float, required=True)
    p = sub.add_parser("link", help="received level and fade margin")
    p.add_argument("--tx", type=float, required=True, help="transmit power dBm")
    p.add_argument("--tx-gain", type=float, default=0.0, help="dBi")
    p.add_argument("--rx-gain", type=float, default=0.0, help="dBi")
    p.add_argument("--km", type=float, required=True)
    p.add_argument("--mhz", type=float, required=True)
    p.add_argument("--losses", type=float, default=0.0, help="cables, radome, rain (dB)")
    p.add_argument("--sens", type=float, required=True, help="receiver sensitivity dBm")
    p = sub.add_parser("fresnel", help="Fresnel zone and clearance at mid-path")
    p.add_argument("--km", type=float, required=True)
    p.add_argument("--ghz", type=float, required=True)
    p = sub.add_parser("horizon", help="radio horizon of an antenna")
    p.add_argument("--height", type=float, required=True, help="metres")
    p.add_argument("--k", type=float, default=STANDARD_K)
    args = parser.parse_args(argv)

    if args.cmd == "fspl":
        print(f"FSPL = {fspl_db(args.km, args.mhz):.2f} dB")
    elif args.cmd == "link":
        rx = received_power_dbm(args.tx, args.tx_gain, args.rx_gain, args.km, args.mhz, args.losses)
        margin = fade_margin_db(rx, args.sens)
        print(f"EIRP {eirp_dbm(args.tx, args.tx_gain):.1f} dBm, rx {rx:.1f} dBm, "
              f"fade margin {margin:.1f} dB")
    elif args.cmd == "fresnel":
        r = fresnel_radius_m(args.km / 2, args.km / 2, args.ghz)
        print(f"zone 1 radius at mid-path {r:.2f} m; clear {clearance_height_m(args.km, args.ghz):.2f} m "
              f"above obstacles (60 % zone 1 + earth bulge)")
    else:
        print(f"radio horizon = {radio_horizon_km(args.height, args.k):.1f} km")


if __name__ == "__main__":
    main()
