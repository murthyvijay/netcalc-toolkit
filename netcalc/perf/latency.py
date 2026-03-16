"""One-way latency budget: serialization, propagation, and per-hop delay.

End-to-end latency is the sum of four kinds of delay:

* **serialization**: clocking the bits of a packet onto the wire,
  ``bits / rate``; paid once per store-and-forward hop
* **propagation**: distance over the signal speed in the medium,
  about 4.9 us per km in fibre (refractive index ~1.468)
* **processing**: lookup and forwarding inside each device
* **queueing**: time spent waiting behind other packets

Usage::

    python -m netcalc.perf.latency serialization --size 1500 --rate 10G
    python -m netcalc.perf.latency propagation --km 100
    python -m netcalc.perf.latency path --size 9000 --rate 400G --hops 3 --km 2 --proc 600ns
"""

import argparse

from netcalc.units import (FIBER_REFRACTIVE_INDEX, SPEED_OF_LIGHT_M_S, fmt_time,
                           parse_rate, parse_size, parse_time)


def serialization_delay(size_bytes, rate_bps):
    """Seconds to clock ``size_bytes`` onto a link of ``rate_bps``.

    >>> serialization_delay(1500, 10e9)
    1.2e-06
    """
    return size_bytes * 8 / rate_bps
