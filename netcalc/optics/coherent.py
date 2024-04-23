"""Coherent line rates: baud, modulation, polarisation, FEC and spectral efficiency.

A coherent transceiver sends symbols on two polarisations::

    line rate = baud * bits_per_symbol * polarizations
    net rate  = line rate / ((1 + FEC overhead) * (1 + framing overhead))
    occupied  = baud * (1 + roll-off)                 (Nyquist-shaped spectrum)
    SE        = net rate / channel spacing            (b/s/Hz)

For example 400ZR runs DP-16QAM at 59.84 GBd: ``59.84 * 4 * 2 = 478.75``
Gb/s on the line, which carries 400GbE after concatenated FEC (about
14.8 %) and framing. Probabilistic constellation shaping (PCS) gives a
fractional number of bits per symbol, so this module accepts a float too.

Usage::

    python -m netcalc.optics.coherent rate --baud 59.84 --mod 16qam --fec 0.148
    python -m netcalc.optics.coherent baud --net 800 --mod 16qam --fec 0.15
    python -m netcalc.optics.coherent capacity --net 400 --spacing 75
"""

import argparse
import math

MODULATION_BITS = {"bpsk": 1, "qpsk": 2, "8qam": 3, "16qam": 4, "32qam": 5, "64qam": 6}
C_BAND_GHZ = 4800.0


def bits_per_symbol(modulation):
    """Bits per symbol per polarisation for a name (``"16qam"``) or a number.

    >>> bits_per_symbol("16QAM"), bits_per_symbol(3.5)
    (4, 3.5)
    """
    if isinstance(modulation, str):
        key = modulation.lower().replace("dp-", "").replace("-", "")
        if key in MODULATION_BITS:
            return MODULATION_BITS[key]
        return float(key)
    return modulation


def line_rate_gbps(baud_g, modulation, polarizations=2):
    """Raw line rate (Gb/s) before FEC and framing are removed."""
    return baud_g * bits_per_symbol(modulation) * polarizations


def net_rate_gbps(baud_g, modulation, polarizations=2, fec_overhead=0.15, framing_overhead=0.0):
    """Client (net) rate in Gb/s after FEC and framing overhead."""
    line = line_rate_gbps(baud_g, modulation, polarizations)
    return line / ((1 + fec_overhead) * (1 + framing_overhead))


def required_baud(net_gbps, modulation, polarizations=2, fec_overhead=0.15, framing_overhead=0.0):
    """Symbol rate (GBd) needed to carry ``net_gbps``."""
    gross = net_gbps * (1 + fec_overhead) * (1 + framing_overhead)
    return gross / (bits_per_symbol(modulation) * polarizations)


def occupied_bandwidth_ghz(baud_g, rolloff=0.1):
    """Spectral width (GHz) of a raised-cosine shaped carrier."""
    return baud_g * (1 + rolloff)


def spectral_efficiency(net_gbps, spacing_ghz):
    """Net spectral efficiency in b/s/Hz."""
    return net_gbps / spacing_ghz


def fiber_capacity_tbps(net_gbps, spacing_ghz, band_ghz=C_BAND_GHZ):
    """Channels that fit in ``band_ghz`` and the total capacity (Tb/s) per fibre."""
    channels = math.floor(band_ghz / spacing_ghz)
    return channels, channels * net_gbps / 1000.0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("rate", help="line and net rate from baud and modulation")
    p.add_argument("--baud", type=float, required=True, help="GBd")
    p.add_argument("--mod", default="16qam", help="qpsk, 8qam, 16qam, 64qam or bits/symbol")
    p.add_argument("--pol", type=int, default=2)
    p.add_argument("--fec", type=float, default=0.15, help="FEC overhead as a fraction")
    p.add_argument("--framing", type=float, default=0.0)
    p.add_argument("--rolloff", type=float, default=0.1)
    p = sub.add_parser("baud", help="baud needed for a net rate")
    p.add_argument("--net", type=float, required=True, help="Gb/s")
    p.add_argument("--mod", default="16qam")
    p.add_argument("--pol", type=int, default=2)
    p.add_argument("--fec", type=float, default=0.15)
    p.add_argument("--framing", type=float, default=0.0)
    p = sub.add_parser("capacity", help="channels and capacity per fibre")
    p.add_argument("--net", type=float, required=True, help="net Gb/s per channel")
    p.add_argument("--spacing", type=float, required=True, help="GHz")
    p.add_argument("--band", type=float, default=C_BAND_GHZ, help="usable spectrum in GHz")
    args = parser.parse_args(argv)

    if args.cmd == "rate":
        line = line_rate_gbps(args.baud, args.mod, args.pol)
        net = net_rate_gbps(args.baud, args.mod, args.pol, args.fec, args.framing)
        occ = occupied_bandwidth_ghz(args.baud, args.rolloff)
        print(f"line {line:.2f} Gb/s, net {net:.2f} Gb/s, occupies {occ:.1f} GHz")
    elif args.cmd == "baud":
        print(f"{required_baud(args.net, args.mod, args.pol, args.fec, args.framing):.2f} GBd")
    else:
        n, tbps = fiber_capacity_tbps(args.net, args.spacing, args.band)
        se = spectral_efficiency(args.net, args.spacing)
        print(f"{n} channels x {args.net:g} Gb/s = {tbps:.1f} Tb/s ({se:.2f} b/s/Hz)")


if __name__ == "__main__":
    main()
