"""IGP convergence budget: detect, flood, compute, program, and the traffic lost meanwhile.

Link-state convergence after a failure is roughly the sum of::

    detection  (BFD: interval x multiplier, or loss of light ~ 10s of ms)
  + origination and flooding  (LSA/LSP generation delay + hops x per-hop flood delay)
  + SPF delay and run time    (initial SPF throttle wait + computation)
  + FIB programming           (prefixes x per-prefix update time)

FIB programming often dominates on large tables, which is why prefix
independent convergence (BGP PIC, pre-computed backup next hops) matters:
it switches every affected prefix by updating one shared next-hop object.
Traffic lost during convergence is simply ``rate x outage``.

Usage::

    python -m netcalc.routing.convergence budget --detect 150ms --hops 4 --prefixes 20000 --per-prefix 20us
    python -m netcalc.routing.convergence loss --outage 300ms --rate 100G
"""

import argparse

from netcalc.units import fmt_size, fmt_time, parse_rate, parse_time
