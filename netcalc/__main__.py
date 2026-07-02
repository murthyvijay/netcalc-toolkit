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
}
