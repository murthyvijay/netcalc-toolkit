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


def virtual_mac(protocol, group):
    """Virtual MAC address for ``vrrp``, ``vrrp6``, ``hsrp1`` or ``hsrp2`` and a group/VRID.

    >>> virtual_mac("vrrp", 10), virtual_mac("hsrp2", 300)
    ('00:00:5e:00:01:0a', '00:00:0c:9f:f1:2c')
    """
    limits = {"vrrp": 255, "vrrp6": 255, "hsrp1": 255, "hsrp2": 4095}
    if protocol not in limits or not 0 <= group <= limits[protocol]:
        raise ValueError(f"invalid group {group} for {protocol}")
    if protocol == "vrrp":
        return f"00:00:5e:00:01:{group:02x}"
    if protocol == "vrrp6":
        return f"00:00:5e:00:02:{group:02x}"
    if protocol == "hsrp1":
        return f"00:00:0c:07:ac:{group:02x}"
    return f"00:00:0c:9f:f{group >> 8:x}:{group & 0xFF:02x}"


def failover_time(detect_s, arp_update_s=0.05):
    """Approximate outage (s) seen by hosts: detection plus gratuitous-ARP propagation."""
    return detect_s + arp_update_s


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("vrrp", help="VRRPv3 master down interval")
    p.add_argument("--interval", type=float, default=VRRP_DEFAULT_INTERVAL_S, help="seconds")
    p.add_argument("--priority", type=int, default=100)
    p = sub.add_parser("hsrp", help="check HSRP hello/hold timers")
    p.add_argument("--hello", type=float, default=HSRP_DEFAULT_HELLO_S)
    p.add_argument("--hold", type=float, default=HSRP_DEFAULT_HOLD_S)
    p = sub.add_parser("mac", help="virtual MAC address")
    p.add_argument("--protocol", choices=("vrrp", "vrrp6", "hsrp1", "hsrp2"), default="vrrp")
    p.add_argument("--group", type=int, required=True)
    args = parser.parse_args(argv)

    if args.cmd == "vrrp":
        down = vrrp_master_down_interval(args.priority, args.interval)
        print(f"skew {vrrp_skew_time(args.priority, args.interval):.4f} s, master down interval "
              f"{down:.4f} s, host outage ~{failover_time(down):.2f} s")
    elif args.cmd == "hsrp":
        ok = "OK" if hsrp_hold_ok(args.hello, args.hold) else "hold should be >= 3 x hello"
        print(f"hello {args.hello:g} s, hold {args.hold:g} s: {ok}; "
              f"host outage ~{failover_time(args.hold):.2f} s")
    else:
        print(virtual_mac(args.protocol, args.group))


if __name__ == "__main__":
    main()
