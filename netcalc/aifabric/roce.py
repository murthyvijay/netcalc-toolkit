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
