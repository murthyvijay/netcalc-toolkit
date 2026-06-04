"""RoCEv2 lossless-Ethernet math: PFC headroom, pause quanta, ECN and DCQCN.

**PFC headroom.** When a switch queue crosses its XOFF threshold it sends
a PAUSE frame upstream, but data keeps arriving until the pause takes
effect. The headroom must absorb::

    2 * cable delay * rate          (round trip on the wire)
  + 2 * MTU                         (frame in flight at each end)
  + PFC response time * rate        (peer reaction, ~ a few quanta)
  + PFC frame size

**ECN marking** (RED/WRED-style): probability 0 below Kmin, rising
linearly to Pmax at Kmax, 1 above Kmax.

**DCQCN** (Zhu et al., SIGCOMM 2015) reacts to Congestion Notification
Packets (CNPs)::

    alpha <- (1 - g) * alpha + g          on CNP (decays when none arrive)
    Rt <- Rc;  Rc <- Rc * (1 - alpha / 2)
    recovery: Rc <- (Rt + Rc) / 2         (fast recovery, F stages)
              Rt <- Rt + R_AI             (then additive increase)

Usage::

    python -m netcalc.aifabric.roce headroom --rate 400G --cable 100m --mtu 4096
    python -m netcalc.aifabric.roce quanta --rate 100G --quanta 65535
    python -m netcalc.aifabric.roce ecn --queue 150KB --kmin 100KB --kmax 400KB --pmax 0.2
    python -m netcalc.aifabric.roce dcqcn --rate 400G --cnps 5 --steps 20
"""

import argparse

from netcalc.units import (FIBER_REFRACTIVE_INDEX, SPEED_OF_LIGHT_M_S, fmt_rate, fmt_size,
                           fmt_time, parse_rate, parse_size, parse_time)

PFC_FRAME_BYTES = 64
QUANTUM_BITS = 512


def cable_delay(length_m, refractive_index=FIBER_REFRACTIVE_INDEX):
    """One-way propagation delay of a cable in seconds."""
    return length_m * refractive_index / SPEED_OF_LIGHT_M_S


def pfc_headroom(rate_bps, cable_m, mtu_bytes=4096, response_s=1e-6,
                 refractive_index=FIBER_REFRACTIVE_INDEX):
    """Per-priority PFC headroom estimate in bytes (see module docstring).

    ``response_s`` lumps the PHY/MAC and peer pause-processing delay; check
    your switch vendor's numbers for production configs.
    """
    wire = 2 * cable_delay(cable_m, refractive_index) * rate_bps / 8
    response = response_s * rate_bps / 8
    return wire + 2 * mtu_bytes + response + PFC_FRAME_BYTES


def pause_time(quanta, rate_bps):
    """Duration of a PFC pause: one quantum is 512 bit times."""
    return quanta * QUANTUM_BITS / rate_bps


def ecn_mark_probability(queue_bytes, kmin_bytes, kmax_bytes, pmax):
    """RED-style ECN marking probability for an instantaneous queue depth."""
    if queue_bytes <= kmin_bytes:
        return 0.0
    if queue_bytes >= kmax_bytes:
        return 1.0
    return (queue_bytes - kmin_bytes) / (kmax_bytes - kmin_bytes) * pmax


def dcqcn_trace(line_rate_bps, cnp_steps, steps, g=1 / 256, rate_ai_bps=None,
                fast_recovery_stages=5, alpha=1.0):
    """Simulate DCQCN's sending rate over ``steps`` timer periods.

    ``cnp_steps`` is a set of step indices at which a CNP arrives. Between
    CNPs the rate recovers: fast recovery for ``fast_recovery_stages``
    periods, then additive increase by ``rate_ai_bps`` (default 0.5 % of line
    rate). Returns a list of ``(step, rate_bps, alpha)``.
    """
    rate_ai = rate_ai_bps or line_rate_bps * 0.005
    rc = rt = line_rate_bps
    since_cut = 0
    trace = []
    for step in range(steps):
        if step in cnp_steps:
            alpha = (1 - g) * alpha + g
            rt = rc
            rc = rc * (1 - alpha / 2)
            since_cut = 0
        else:
            alpha = (1 - g) * alpha
            since_cut += 1
            if since_cut > fast_recovery_stages:
                rt = min(line_rate_bps, rt + rate_ai)
            rc = min(line_rate_bps, (rt + rc) / 2)
        trace.append((step, rc, alpha))
    return trace
