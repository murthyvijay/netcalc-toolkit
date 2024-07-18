"""M/G/1 and G/G/1 waiting times: why packet-size and burst variability matter.

The Pollaczek-Khinchine formula gives the mean wait in queue of an M/G/1
system with utilisation ``rho``, mean service time ``E[S]`` and squared
coefficient of variation of service ``cs2 = Var[S] / E[S]^2``::

    Wq = rho / (1 - rho) * (1 + cs2) / 2 * E[S]

``cs2 = 1`` is M/M/1, ``cs2 = 0`` is M/D/1 (fixed-size cells: half the
wait). Kingman's approximation extends it to bursty arrivals with arrival
variability ``ca2``::

    Wq ~ rho / (1 - rho) * (ca2 + cs2) / 2 * E[S]

For a packet mix, ``E[S]`` and ``cs2`` come from the size distribution at
the link rate.

Usage::

    python -m netcalc.queueing.mg1 wait --rate 10G --load 0.7 --size 1000 --cs2 0
    python -m netcalc.queueing.mg1 mix --rate 10G --load 0.7 64:7 576:4 1500:1
    python -m netcalc.queueing.mg1 kingman --rate 10G --load 0.7 --size 1000 --ca2 4 --cs2 1
"""

import argparse

from netcalc.units import fmt_time, parse_rate
