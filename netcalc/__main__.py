"""List every netcalc tool, or run one: ``python -m netcalc <tool> [args]``.

Examples::

    python -m netcalc                      # list tools
    python -m netcalc fec info --code kp4  # same as python -m netcalc.layer1.fec info --code kp4
"""

import importlib
import sys

TOOLS = {
    "ber": "netcalc.layer1.ber",
    "qfactor": "netcalc.layer1.qfactor",
    "fec": "netcalc.layer1.fec",
    "ser": "netcalc.layer1.ser",
    "osnr": "netcalc.layer1.osnr",
    "latency": "netcalc.perf.latency",
    "jitter": "netcalc.perf.jitter",
    "loss": "netcalc.perf.loss",
    "throughput": "netcalc.perf.throughput",
    "tcp": "netcalc.perf.tcp",
    "subnet": "netcalc.ccna.subnet",
    "vlsm": "netcalc.ccna.vlsm",
    "wildcard": "netcalc.ccna.wildcard",
    "summarize": "netcalc.ccna.summarize",
    "ospf": "netcalc.ccna.ospf",
    "eigrp": "netcalc.ccna.eigrp",
    "stp": "netcalc.ccna.stp",
    "qos": "netcalc.ccna.qos",
    "overhead": "netcalc.protocols.overhead",
    "mtu": "netcalc.protocols.mtu",
    "loadbalance": "netcalc.aifabric.loadbalance",
    "retransmit": "netcalc.aifabric.retransmit",
    "mrc": "netcalc.aifabric.mrc",
    "roce": "netcalc.aifabric.roce",
    "buffer": "netcalc.aifabric.buffer",
    "collectives": "netcalc.aifabric.collectives",
    "dwdm": "netcalc.optics.dwdm",
    "budget": "netcalc.optics.budget",
    "dispersion": "netcalc.optics.dispersion",
    "coherent": "netcalc.optics.coherent",
    "amplifier": "netcalc.optics.amplifier",
    "rf": "netcalc.wireless.rf",
    "capacity": "netcalc.wireless.capacity",
    "wifi": "netcalc.wireless.wifi",
    "littles": "netcalc.queueing.littles",
    "erlang": "netcalc.queueing.erlang",
    "mg1": "netcalc.queueing.mg1",
    "mm1k": "netcalc.queueing.mm1k",
    "dscp": "netcalc.traffic.dscp",
    "marker": "netcalc.traffic.marker",
}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help", "list"):
        print("usage: python -m netcalc <tool> [args]   (or: netcalc <tool> [args])\n")
        for name, module in TOOLS.items():
            doc = (importlib.import_module(module).__doc__ or "").strip().split("\n")[0]
            print(f"  {name:<12} {doc}")
        return 0
    if argv[0] not in TOOLS:
        print(f"unknown tool {argv[0]!r}; run without arguments to list tools", file=sys.stderr)
        return 2
    importlib.import_module(TOOLS[argv[0]]).main(argv[1:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
