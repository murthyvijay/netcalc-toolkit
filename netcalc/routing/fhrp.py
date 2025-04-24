"""First-hop redundancy: VRRP and HSRP timers, virtual MACs and failover time.

* **VRRPv3** (RFC 5798): the master advertises every ``Advertisement_Interval``
  (default 1 s). A backup takes over after the master down interval::

      Master_Down_Interval = 3 * Advertisement_Interval + Skew_Time
      Skew_Time = ((256 - priority) * Advertisement_Interval) / 256

  so higher-priority backups react first. The virtual MAC is
  ``00:00:5e:00:01:<VRID>`` (``00:00:5e:00:02:<VRID>`` for IPv6).
* **HSRP** (Cisco): hello 3 s and hold 10 s by default; version 1 uses
  ``00:00:0c:07:ac:<group>`` and version 2 ``00:00:0c:9f:f<group>`` (12-bit
  group).

Failover time is roughly the down/hold interval plus the time for the new
master's gratuitous ARP to update the switches.

Usage::

    python -m netcalc.routing.fhrp vrrp --interval 1 --priority 100
    python -m netcalc.routing.fhrp mac --protocol hsrp2 --group 300
"""

import argparse

VRRP_DEFAULT_INTERVAL_S = 1.0
HSRP_DEFAULT_HELLO_S = 3.0
HSRP_DEFAULT_HOLD_S = 10.0


def vrrp_skew_time(priority, interval_s=VRRP_DEFAULT_INTERVAL_S):
    """VRRPv3 skew time (s) for a backup of ``priority`` (1..254)."""
    if not 1 <= priority <= 255:
        raise ValueError("VRRP priority must be 1..255")
    return (256 - priority) * interval_s / 256


def vrrp_master_down_interval(priority, interval_s=VRRP_DEFAULT_INTERVAL_S):
    """Time (s) a VRRPv3 backup waits before taking over.

    >>> vrrp_master_down_interval(100, 1.0)
    3.609375
    """
    return 3 * interval_s + vrrp_skew_time(priority, interval_s)


def hsrp_hold_ok(hello_s, hold_s):
    """True if the HSRP hold time is at least three hellos, as recommended."""
    return hold_s >= 3 * hello_s
