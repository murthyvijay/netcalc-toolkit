"""M/M/1/K: loss and delay in a finite buffer of K packets.

With offered load ``rho = lambda / mu`` and room for K packets (including
the one in service) the stationary distribution is geometric and truncated::

    P(n) = (1 - rho) rho^n / (1 - rho^(K+1))      (rho != 1)
    P(n) = 1 / (K + 1)                            (rho == 1)

An arrival that finds the buffer full is dropped, so the loss probability is
``P(K)`` and carried throughput is ``lambda (1 - P(K))``. Unlike M/M/1, the
system is stable even above 100 % load: it simply drops the excess. Turning
the formula around gives the buffer needed for a loss target.

Usage::

    python -m netcalc.queueing.mm1k loss --load 0.9 --k 20
    python -m netcalc.queueing.mm1k size --load 0.9 --loss 1e-6
"""

import argparse
import math
