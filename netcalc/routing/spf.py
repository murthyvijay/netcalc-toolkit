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


def parse_edges(items, directed=False):
    """Build ``{node: {neighbor: cost}}`` from ``["A-B:10", ...]``."""
    graph = {}
    for item in items:
        link, _, cost = item.partition(":")
        a, b = link.split("-", 1)
        cost = float(cost) if cost else 1.0
        graph.setdefault(a, {})[b] = cost
        graph.setdefault(b, {})
        if not directed:
            graph[b][a] = cost
    return graph


def dijkstra(graph, src):
    """Distances from ``src`` and every equal-cost predecessor of each node."""
    dist = {src: 0.0}
    preds = {src: []}
    heap = [(0.0, src)]
    done = set()
    while heap:
        d, node = heapq.heappop(heap)
        if node in done:
            continue
        done.add(node)
        for nbr, cost in graph.get(node, {}).items():
            nd = d + cost
            if nbr not in dist or nd < dist[nbr] - 1e-12:
                dist[nbr] = nd
                preds[nbr] = [node]
                heapq.heappush(heap, (nd, nbr))
            elif abs(nd - dist[nbr]) <= 1e-12 and node not in preds[nbr]:
                preds[nbr].append(node)
    return dist, preds


def all_paths(preds, src, dst):
    """Every equal-cost shortest path from ``src`` to ``dst`` as node lists."""
    if dst == src:
        return [[src]]
    if dst not in preds:
        return []
    return [path + [dst] for p in sorted(preds[dst]) for path in all_paths(preds, src, p)]


def next_hops(graph, src, dst):
    """ECMP next hops from ``src`` towards ``dst``.

    >>> g = parse_edges(["A-B:10", "B-D:10", "A-C:10", "C-D:10"])
    >>> next_hops(g, "A", "D")
    ['B', 'C']
    """
    _, preds = dijkstra(graph, src)
    return sorted({path[1] for path in all_paths(preds, src, dst) if len(path) > 1})


def loop_free_alternates(graph, src, dst):
    """Neighbours of ``src`` that are LFAs to ``dst``: ``[(neighbor, node_protecting)]``."""
    dist_s, _ = dijkstra(graph, src)
    primary = next_hops(graph, src, dst)
    result = []
    for nbr in sorted(graph[src]):
        if nbr in primary:
            continue
        dist_n, _ = dijkstra(graph, nbr)
        if dist_n.get(dst, float("inf")) < dist_n[src] + dist_s[dst]:
            protecting = all(
                dist_n[dst] < dist_n.get(e, float("inf")) + dijkstra(graph, e)[0].get(dst, float("inf"))
                for e in primary if e != dst)
            result.append((nbr, protecting))
    return result
