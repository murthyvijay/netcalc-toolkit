"""DSCP, per-hop behaviours, ToS bytes and 802.1p CoS.

The 6-bit DSCP sits in the top of the IPv4 ToS / IPv6 Traffic Class byte,
above the 2 ECN bits: ``tos = dscp << 2 | ecn``. Standard code points:

* Class Selector ``CSx = 8 x`` (backwards compatible with IP precedence x)
* Assured Forwarding ``AFxy = 8 x + 2 y`` (class x = 1..4, drop precedence
  y = 1..3; higher y is dropped first under congestion)
* Expedited Forwarding ``EF = 46``, Voice-Admit ``VA = 44``,
  Lower-Effort ``LE = 1`` (RFC 8622), Default ``DF = 0``

RFC 4594 recommends a code point per service class; the usual default
802.1p CoS for a DSCP is its top three bits.

Usage::

    python -m netcalc.traffic.dscp lookup AF41
    python -m netcalc.traffic.dscp lookup 46
    python -m netcalc.traffic.dscp tos 0xb8
    python -m netcalc.traffic.dscp table
"""

import argparse

NAMED = {"DF": 0, "LE": 1, "EF": 46, "VA": 44}
NAMED.update({f"CS{x}": 8 * x for x in range(8)})
NAMED.update({f"AF{x}{y}": 8 * x + 2 * y for x in range(1, 5) for y in range(1, 4)})

RFC4594_CLASSES = {
    "Network Control": "CS6",
    "Telephony": "EF",
    "Signaling": "CS5",
    "Multimedia Conferencing": "AF41",
    "Real-Time Interactive": "CS4",
    "Multimedia Streaming": "AF31",
    "Broadcast Video": "CS3",
    "Low-Latency Data": "AF21",
    "OAM": "CS2",
    "High-Throughput Data": "AF11",
    "Standard": "DF",
    "Low-Priority Data": "LE",
}


def parse_dscp(value):
    """DSCP number from a name (``"AF41"``), a decimal string or an int.

    >>> parse_dscp("af41"), parse_dscp("46"), parse_dscp(10)
    (34, 46, 10)
    """
    if isinstance(value, int):
        dscp = value
    else:
        text = str(value).strip().upper()
        dscp = NAMED[text] if text in NAMED else int(text, 0)
    if not 0 <= dscp <= 63:
        raise ValueError("DSCP must be 0..63")
    return dscp


def phb_name(dscp):
    """Per-hop behaviour name of a DSCP, or ``"EXP/LU"`` for unassigned values.

    >>> phb_name(34), phb_name(48), phb_name(5)
    ('AF41', 'CS6', 'EXP/LU')
    """
    for name, value in NAMED.items():
        if value == dscp and name != "CS0":
            return name
    return "EXP/LU"


def dscp_to_tos(dscp, ecn=0):
    """ToS / Traffic Class byte for a DSCP and ECN codepoint."""
    return (parse_dscp(dscp) << 2) | (ecn & 0b11)


def tos_to_dscp(tos):
    """Split a ToS byte into ``(dscp, ecn)``."""
    return tos >> 2, tos & 0b11


def ip_precedence(dscp):
    """Legacy IP precedence (top three bits of the DSCP)."""
    return parse_dscp(dscp) >> 3


def af_drop_precedence(dscp):
    """AF drop precedence (1 low .. 3 high), or ``None`` for non-AF code points."""
    name = phb_name(parse_dscp(dscp))
    return int(name[3]) if name.startswith("AF") else None


def default_cos(dscp):
    """Default 802.1p / MPLS TC value for a DSCP (its class bits)."""
    return ip_precedence(dscp)
