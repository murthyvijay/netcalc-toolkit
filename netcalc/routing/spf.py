"""Shortest path first (Dijkstra) with ECMP, and loop-free alternates (RFC 5286).

OSPF and IS-IS run Dijkstra over the link-state database: every router
computes the lowest-cost path to every destination from its own point of
view, keeping all equal-cost next hops (ECMP).

For fast reroute, a neighbour N of source S is a **loop-free alternate**
towards destination D if traffic it receives from S cannot come back::

    dist(N, D) < dist(N, S) + dist(S, D)

It is also **node-protecting** if it avoids the primary next hop E:
``dist(N, D) < dist(N, E) + dist(E, D)``.

Usage::

    python -m netcalc.routing.spf paths --src A A-B:10 B-D:10 A-C:10 C-D:10
    python -m netcalc.routing.spf lfa --src S --dst D S-E:10 E-D:10 S-N:10 N-D:15
"""

import argparse
import heapq
