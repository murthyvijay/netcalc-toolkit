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


def amplifier_chain_osnr_db(launch_dbm, span_loss_db, nf_db, spans, constant=58.0):
    """OSNR after ``spans`` identical spans, each followed by an EDFA.

    Each amplifier sees ``launch - span_loss`` at its input, contributing
    ``58 + P_in - NF``; N identical contributions cost ``10 log10(N)``.
    """
    single = constant + (launch_dbm - span_loss_db) - nf_db
    return single - 10 * math.log10(spans)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("to-snr", help="OSNR to electrical SNR")
    p.add_argument("--osnr-db", type=float, required=True)
    p.add_argument("--baud", type=float, required=True, help="symbol rate in GBd")
    p.add_argument("--pol", type=int, default=2)
    p = sub.add_parser("to-osnr", help="electrical SNR to required OSNR")
    p.add_argument("--snr-db", type=float, required=True)
    p.add_argument("--baud", type=float, required=True)
    p.add_argument("--pol", type=int, default=2)
    p = sub.add_parser("chain", help="OSNR of an amplified line")
    p.add_argument("--launch-dbm", type=float, required=True)
    p.add_argument("--span-loss", type=float, required=True)
    p.add_argument("--nf", type=float, default=5.0)
    p.add_argument("--spans", type=int, required=True)
    p = sub.add_parser("cascade", help="combine OSNR contributions")
    p.add_argument("osnr", type=float, nargs="+")
    args = parser.parse_args(argv)

    if args.cmd == "to-snr":
        print(f"SNR = {osnr_to_snr_db(args.osnr_db, args.baud, args.pol):.2f} dB")
    elif args.cmd == "to-osnr":
        print(f"OSNR = {snr_to_osnr_db(args.snr_db, args.baud, args.pol):.2f} dB (0.1 nm)")
    elif args.cmd == "chain":
        o = amplifier_chain_osnr_db(args.launch_dbm, args.span_loss, args.nf, args.spans)
        print(f"end-of-line OSNR = {o:.2f} dB (0.1 nm)")
    else:
        print(f"total OSNR = {cascade_osnr_db(*args.osnr):.2f} dB")


if __name__ == "__main__":
    main()
