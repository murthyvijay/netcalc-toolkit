"""IS-IS addressing and metrics: NETs, system IDs, narrow vs wide metrics, LSP refresh.

* A **NET** (network entity title) is an NSAP with selector 00, written in
  dotted hex: ``49.0001.1921.6800.1001.00`` is AFI 49 (private), area
  0001, system ID 1921.6800.1001 and NSEL 00. A common convention derives
  the system ID from a loopback IPv4 address by zero-padding each octet to
  three digits (192.168.1.1 -> 192168001001 -> 1921.6800.1001).
* **Metrics**: narrow (original) metrics are 6 bits per interface (max 63)
  and 10 bits per path (max 1023), too small to express modern link speeds.
  Wide metrics (RFC 5305) allow 24 bits per interface (max 16,777,215).
  IS-IS has no automatic cost; operators often use ``reference / bandwidth``.
* **LSP refresh**: LSPs live for MaxAge (1200 s by default, up to 65535 s)
  and are refreshed before they expire (900 s by default), so a domain with
  N LSPs carries about ``N / refresh`` LSPs per second of background flooding.

Usage::

    python -m netcalc.routing.isis net 49.0001.1921.6800.1001.00
    python -m netcalc.routing.isis sysid 192.168.1.1 --area 49.0001
    python -m netcalc.routing.isis metric --rate 400G --reference 1T --style wide
    python -m netcalc.routing.isis refresh --lsps 5000 --refresh 900
"""

import argparse
import ipaddress
import math

from netcalc.units import parse_rate

NARROW_INTERFACE_MAX = 63
NARROW_PATH_MAX = 1023
WIDE_INTERFACE_MAX = 2 ** 24 - 1
DEFAULT_MAX_AGE_S = 1200
DEFAULT_REFRESH_S = 900


def parse_net(net):
    """Split a NET into area, system ID and selector.

    >>> parse_net("49.0001.1921.6800.1001.00")
    {'area': '49.0001', 'system_id': '1921.6800.1001', 'nsel': '00'}
    """
    parts = net.lower().split(".")
    if len(parts) < 5 or len(parts[-1]) != 2 or any(len(p) != 4 for p in parts[-4:-1]):
        raise ValueError(f"not a NET: {net!r}")
    return {"area": ".".join(parts[:-4]), "system_id": ".".join(parts[-4:-1]), "nsel": parts[-1]}


def system_id_from_ipv4(address):
    """System ID from an IPv4 loopback by padding each octet to three digits."""
    digits = "".join(f"{int(o):03d}" for o in str(ipaddress.IPv4Address(address)).split("."))
    return ".".join(digits[i:i + 4] for i in range(0, 12, 4))


def make_net(area, system_id, nsel="00"):
    """Assemble a NET from its parts."""
    return f"{area}.{system_id}.{nsel}"


def metric_from_bandwidth(rate_bps, reference_bps=1e12, style="wide"):
    """Interface metric ``ceil(reference / bandwidth)``, clamped to the metric style.

    >>> metric_from_bandwidth(100e9, 1e12), metric_from_bandwidth(1e9, 1e12, "narrow")
    (10, 63)
    """
    limit = WIDE_INTERFACE_MAX if style == "wide" else NARROW_INTERFACE_MAX
    return min(max(1, math.ceil(reference_bps / rate_bps)), limit)


def narrow_path_ok(metrics):
    """True if a path of narrow interface metrics stays within the 1023 path limit."""
    return sum(metrics) <= NARROW_PATH_MAX


def lsp_refresh_rate(lsps, refresh_s=DEFAULT_REFRESH_S):
    """Background LSP regenerations per second across the domain."""
    return lsps / refresh_s


def refresh_is_safe(max_age_s, refresh_s, margin_s=300):
    """True if LSPs are refreshed at least ``margin_s`` before they would age out."""
    return refresh_s <= max_age_s - margin_s


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("net", help="decode a NET")
    p.add_argument("net")
    p = sub.add_parser("sysid", help="system ID and NET from a loopback address")
    p.add_argument("address")
    p.add_argument("--area", default="49.0001")
    p = sub.add_parser("metric", help="interface metric from bandwidth")
    p.add_argument("--rate", required=True)
    p.add_argument("--reference", default="1T")
    p.add_argument("--style", choices=("wide", "narrow"), default="wide")
    p = sub.add_parser("refresh", help="background LSP refresh load")
    p.add_argument("--lsps", type=int, required=True)
    p.add_argument("--refresh", type=float, default=DEFAULT_REFRESH_S)
    p.add_argument("--max-age", type=float, default=DEFAULT_MAX_AGE_S)
    args = parser.parse_args(argv)

    if args.cmd == "net":
        for key, value in parse_net(args.net).items():
            print(f"{key:>10}: {value}")
    elif args.cmd == "sysid":
        sysid = system_id_from_ipv4(args.address)
        print(f"system ID {sysid}, NET {make_net(args.area, sysid)}")
    elif args.cmd == "metric":
        m = metric_from_bandwidth(parse_rate(args.rate), parse_rate(args.reference), args.style)
        print(f"{args.style} metric = {m}")
    else:
        rate = lsp_refresh_rate(args.lsps, args.refresh)
        safe = "safe" if refresh_is_safe(args.max_age, args.refresh) else "too close to MaxAge"
        print(f"{rate:.2f} LSP refreshes/s; refresh {args.refresh:g} s vs MaxAge "
              f"{args.max_age:g} s is {safe}")


if __name__ == "__main__":
    main()
