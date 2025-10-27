"""Plan an amplified DWDM route: spans, power, OSNR, dispersion and capacity.

Combines the optics tools: amplifier span planning and per-channel power,
the Layer 1 OSNR chain, chromatic-dispersion accumulation against a coherent
DSP tolerance, and the channel count and capacity of the C band.

    python examples/optical_span_report.py --km 600 --channels 64 --baud 64 --mod 16qam
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netcalc.layer1 import osnr  # noqa: E402
from netcalc.optics import amplifier, coherent, dispersion, dwdm  # noqa: E402


def plan_route(km, max_span_km=80.0, alpha_db_km=0.22, amp_total_dbm=20.0, nf_db=5.5, channels=64):
    """Spans, per-span loss, launch power per channel and end-of-line OSNR."""
    spans = amplifier.spans_needed(km, max_span_km)
    span_km = km / spans
    span_loss = span_km * alpha_db_km
    launch = amplifier.per_channel_power(amp_total_dbm, channels)
    eol_osnr = osnr.amplifier_chain_osnr_db(launch, span_loss, nf_db, spans)
    return {"spans": spans, "span_km": span_km, "span_loss_db": span_loss,
            "launch_dbm": launch, "osnr_db": eol_osnr}


def carrier_summary(baud_g, modulation, fec_overhead=0.15, rolloff=0.1):
    """Net rate, flexgrid slot and the OSNR-to-SNR conversion for one carrier."""
    net = coherent.net_rate_gbps(baud_g, modulation, fec_overhead=fec_overhead)
    m, slot = dwdm.flex_slot(baud_g, rolloff)
    return {"net_gbps": net, "slot_ghz": slot, "slot_m": m}


def route_report(km, channels, baud_g, modulation, cd_tolerance_ps_nm=50000, required_snr_db=16.0):
    """Return the report lines for an amplified route."""
    route = plan_route(km, channels=channels)
    carrier = carrier_summary(baud_g, modulation)
    snr = osnr.osnr_to_snr_db(route["osnr_db"], baud_g)
    cd = dispersion.accumulated_cd(km)
    fit, capacity = coherent.fiber_capacity_tbps(carrier["net_gbps"], carrier["slot_ghz"])
    lit = min(fit, channels)
    return [
        f"route              {km:g} km in {route['spans']} spans of {route['span_km']:.1f} km "
        f"({route['span_loss_db']:.1f} dB each)",
        f"launch power       {route['launch_dbm']:.2f} dBm per channel ({channels} channels)",
        f"end-of-line OSNR   {route['osnr_db']:.2f} dB (0.1 nm) -> SNR {snr:.2f} dB at "
        f"{baud_g:g} GBd: {'PASS' if snr >= required_snr_db else 'FAIL'} vs {required_snr_db:g} dB",
        f"chromatic disp.    {cd:,.0f} ps/nm: "
        f"{'within' if cd <= cd_tolerance_ps_nm else 'beyond'} DSP tolerance",
        f"carrier            {carrier['net_gbps']:.0f} Gb/s net in a {carrier['slot_ghz']:g} GHz slot",
        f"capacity           {lit} x {carrier['net_gbps']:.0f} Gb/s = "
        f"{lit * carrier['net_gbps'] / 1000:.1f} Tb/s (band fits {fit}, {capacity:.1f} Tb/s)",
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--km", type=float, required=True)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--baud", type=float, default=64.0)
    parser.add_argument("--mod", default="16qam")
    parser.add_argument("--required-snr", type=float, default=16.0)
    args = parser.parse_args()
    print("\n".join(route_report(args.km, args.channels, args.baud, args.mod,
                                 required_snr_db=args.required_snr)))


if __name__ == "__main__":
    main()
