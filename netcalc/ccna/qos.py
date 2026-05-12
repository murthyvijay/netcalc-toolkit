"""QoS math: queueing delay, CBWFQ shares, policing and shaping.

* **M/M/1 queue**: with arrival rate lambda and service rate mu
  (utilisation rho = lambda / mu) the mean wait in queue is
  ``rho / (mu - lambda)`` and the mean number queued ``rho^2 / (1 - rho)``.
  Delay explodes as rho approaches 1, which is why links are planned for
  well under 100 % utilisation.
* **CBWFQ**: each class gets its configured share of the link when
  congested; priority (LLQ) traffic is served first but policed.
* **Token bucket**: shaping interval ``Tc = Bc / CIR``; Cisco recommends a
  policer burst of 1.5 seconds of traffic (``Bc = CIR / 8 * 1.5`` bytes).

Usage::

    python -m netcalc.ccna.qos mm1 --rate 1G --load 0.8 --size 1000
    python -m netcalc.ccna.qos cbwfq --rate 10G VOICE=10 VIDEO=30 DATA=40
    python -m netcalc.ccna.qos shaper --cir 50M --bc 200000
"""

import argparse

from netcalc.units import fmt_rate, fmt_time, parse_rate, parse_size
