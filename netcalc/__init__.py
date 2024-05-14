"""netcalc: stdlib-only calculators for network engineers.

Subpackages:

* ``netcalc.layer1``    BER, Q-factor, Reed-Solomon FEC, SER, OSNR
* ``netcalc.perf``      latency, jitter, packet loss, throughput, TCP models
* ``netcalc.ccna``      subnetting, VLSM, wildcards, summarization, OSPF, EIGRP, STP, QoS
* ``netcalc.protocols`` header overhead, goodput, MTU/MSS
* ``netcalc.aifabric``  load balancing, retransmission, MRC, RoCE/PFC/DCQCN, buffers, collectives
* ``netcalc.optics``    DWDM grid, power budget, dispersion, coherent line rates, amplifiers
* ``netcalc.wireless``  RF link budget, Shannon capacity and noise, Wi-Fi channels and PHY rates

Every module is also a command-line tool: ``python -m netcalc.<package>.<module> --help``.
"""

__version__ = "1.0.0"
