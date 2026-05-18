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
