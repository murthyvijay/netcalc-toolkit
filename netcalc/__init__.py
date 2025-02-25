"""netcalc: stdlib-only calculators for network engineers.

Subpackages:

* ``netcalc.layer1``    BER, Q-factor, Reed-Solomon FEC, SER, OSNR
* ``netcalc.perf``      latency, jitter, packet loss, throughput, TCP models
* ``netcalc.ccna``      subnetting, VLSM, wildcards, summarization, OSPF, EIGRP, STP, QoS
* ``netcalc.protocols`` header overhead, goodput, MTU/MSS
* ``netcalc.aifabric``  load balancing, retransmission, MRC, RoCE/PFC/DCQCN, buffers, collectives
* ``netcalc.optics``    DWDM grid, power budget, dispersion, coherent line rates, amplifiers
* ``netcalc.wireless``  RF link budget, Shannon capacity and noise, Wi-Fi channels and PHY rates
* ``netcalc.queueing``  Little's law, Erlang B/C, M/G/1 and Kingman, M/M/1/K buffers
* ``netcalc.traffic``   DSCP/PHB mapping, srTCM/trTCM policers, WRED, max-min fair schedulers
* ``netcalc.routing``   BGP, SPF/ECMP/LFA, IS-IS, BFD, VRRP/HSRP, MPLS/SR, EVPN, convergence

Every module is also a command-line tool: ``python -m netcalc.<package>.<module> --help``.
"""

__version__ = "1.0.0"
