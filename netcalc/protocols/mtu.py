"""MTU, MSS and encapsulation headroom.

* TCP MSS = IP MTU - IP header - TCP header (- TCP options)
* An overlay steals bytes from the underlay MTU: VXLAN over IPv4 adds
  50 bytes (outer Ethernet 14 + IPv4 20 + UDP 8 + VXLAN 8), so a 1500-byte
  tenant MTU needs a 1550-byte underlay IP MTU (1600 or 9216 in practice).
* RoCEv2 picks a path MTU from {256, 512, 1024, 2048, 4096} that must fit in
  the Ethernet MTU together with IP/UDP/BTH/ICRC headers.

Usage::

    python -m netcalc.protocols.mtu mss --mtu 1500
    python -m netcalc.protocols.mtu mss --mtu 9000 --ipv6 --timestamps
    python -m netcalc.protocols.mtu overlay --inner-mtu 1500 vxlan
    python -m netcalc.protocols.mtu effective --mtu 1500 gre ipsec
    python -m netcalc.protocols.mtu roce --mtu 9000
"""

import argparse

ENCAP_BYTES = {
    "dot1q": 4,
    "qinq": 8,
    "mpls": 4,
    "vxlan": 50,        # outer eth 14 + ipv4 20 + udp 8 + vxlan 8
    "vxlan6": 70,       # IPv6 underlay
    "geneve": 50,       # without options
    "gre": 24,          # outer ipv4 20 + gre 4
    "ipsec": 73,        # ESP tunnel, AES-CBC + SHA1 worst case (approximate)
    "wireguard": 60,    # ipv4 20 + udp 8 + wg 32
    "srv6": 40,         # outer ipv6 without SRH
    "pppoe": 8,
}

ROCE_MTUS = (256, 512, 1024, 2048, 4096)
ROCE_HEADERS = 20 + 8 + 12 + 4  # IPv4 + UDP + BTH + ICRC


def mss(mtu, ipv6=False, timestamps=False, extra_options=0):
    """TCP maximum segment size for an IP MTU."""
    ip_header = 40 if ipv6 else 20
    options = (12 if timestamps else 0) + extra_options
    return mtu - ip_header - 20 - options


def encap_overhead(*encaps):
    """Total bytes added by a list of encapsulations."""
    unknown = [e for e in encaps if e not in ENCAP_BYTES]
    if unknown:
        raise ValueError(f"unknown encapsulations: {unknown}")
    return sum(ENCAP_BYTES[e] for e in encaps)


def effective_mtu(mtu, *encaps):
    """Inner MTU left after carrying ``encaps`` over a link of ``mtu``."""
    return mtu - encap_overhead(*encaps)


def required_underlay_mtu(inner_mtu, *encaps):
    """Underlay MTU needed to carry ``inner_mtu`` without fragmentation."""
    return inner_mtu + encap_overhead(*encaps)


def roce_path_mtu(ethernet_mtu, ipv6=False):
    """Largest RoCE path MTU that fits in an Ethernet (IP) MTU."""
    headers = ROCE_HEADERS + (20 if ipv6 else 0)
    fitting = [m for m in ROCE_MTUS if m + headers <= ethernet_mtu]
    if not fitting:
        raise ValueError("Ethernet MTU too small for RoCE")
    return fitting[-1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("mss")
    p.add_argument("--mtu", type=int, default=1500)
    p.add_argument("--ipv6", action="store_true")
    p.add_argument("--timestamps", action="store_true")
    p = sub.add_parser("overlay", help="underlay MTU required for an overlay")
    p.add_argument("--inner-mtu", type=int, default=1500)
    p.add_argument("encaps", nargs="+", choices=sorted(ENCAP_BYTES))
    p = sub.add_parser("effective", help="inner MTU left after encapsulation")
    p.add_argument("--mtu", type=int, default=1500)
    p.add_argument("encaps", nargs="+", choices=sorted(ENCAP_BYTES))
    p = sub.add_parser("roce", help="RoCE path MTU for an Ethernet MTU")
    p.add_argument("--mtu", type=int, default=9000)
    p.add_argument("--ipv6", action="store_true")
    args = parser.parse_args(argv)

    if args.cmd == "mss":
        print(f"MSS = {mss(args.mtu, args.ipv6, args.timestamps)} bytes")
    elif args.cmd == "overlay":
        print(f"underlay MTU >= {required_underlay_mtu(args.inner_mtu, *args.encaps)}")
    elif args.cmd == "effective":
        print(f"effective MTU = {effective_mtu(args.mtu, *args.encaps)}")
    else:
        print(f"RoCE path MTU = {roce_path_mtu(args.mtu, args.ipv6)}")


if __name__ == "__main__":
    main()
