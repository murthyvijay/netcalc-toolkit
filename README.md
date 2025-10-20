# netcalc-toolkit

Small, dependency-free Python calculators for network engineers: Layer 1
link budgets and FEC, latency/jitter/loss, CCNA/CCNP subnetting and routing
metrics, protocol overhead, and AI/ML fabric sizing (multipath transport,
Ultra Ethernet-style spraying, RoCE/PFC/DCQCN, buffers, collectives).

* **Standard library only.** Python 3.9+, nothing to `pip install` to run it.
* **Every module is both a library and a CLI.** Import the functions, or run
  `python -m netcalc <tool> --help`.
* **Formulas are documented.** Each module's docstring shows the equation it
  implements, and [TECHNOLOGY.md](TECHNOLOGY.md) explains the concepts.
* **Tested.** 140+ unit tests under `tests/`.

## Install

```bash
git clone https://github.com/murthyvijay/netcalc-toolkit.git
cd netcalc-toolkit

# run straight from the checkout ...
python -m netcalc

# ... or install the `netcalc` command
pip install .
netcalc fec info --code kp4
```

Run the tests with `python -m unittest discover -s tests -t .`

## Quick start

```bash
$ netcalc fec margin --code kp4 --pre-ber 1e-6
threshold 2.771e-04, margin 2.44 decades, 2.78 dB Q -> PASS

$ netcalc subnet info 192.168.10.77/26
         network: 192.168.10.64
       broadcast: 192.168.10.127
      first_host: 192.168.10.65
       last_host: 192.168.10.126
    usable_hosts: 62
             ...

$ netcalc loadbalance imbalance --flows 64 --paths 64
busiest path carries 3.93x the even share; effective throughput 25.5%
```

In Python:

```python
from netcalc.layer1 import fec
from netcalc.perf import tcp

fec.pre_fec_threshold("kp4", target_post_ber=1e-13)   # 2.77e-04
tcp.mathis_throughput(mss_bytes=1460, rtt_s=0.05, loss=1e-4)  # ~28.6 Mbps
```

Rates, sizes and times accept friendly strings everywhere on the command
line: `100G`, `25Gbps`, `9KB`, `2MiB`, `10ms`, `600ns`.

## Tools

### Layer 1 (`netcalc.layer1`)

| tool | what it answers | example |
|---|---|---|
| `ber` | measured BER, bits/time needed to claim a BER at a confidence level | `netcalc ber time --target 1e-12 --rate 100G` |
| `qfactor` | Q-factor to BER and back, Q in dB, Q from eye levels | `netcalc qfactor to-q 1e-12` |
| `fec` | RS(n,k) correction capability, post-FEC BER, pre-FEC threshold, FEC margin, net coding gain (KR4/KP4 presets) | `netcalc fec post --code kp4 --pre-ber 2e-4` |
| `ser` | symbol error rate for PAM-M and QAM-M, Gray-coded BER, Eb/N0 to Es/N0 | `netcalc ser pam --levels 4 --snr-db 20` |
| `osnr` | OSNR to electrical SNR, amplified-line OSNR, cascading OSNR | `netcalc osnr chain --launch-dbm 1 --span-loss 22 --nf 5.5 --spans 10` |

### Performance (`netcalc.perf`)

| tool | what it answers | example |
|---|---|---|
| `latency` | serialization, propagation, store-and-forward vs cut-through path latency | `netcalc latency path --size 9000 --rate 400G --hops 3 --km 2 --proc 600ns` |
| `jitter` | RFC 3550 interarrival jitter, IPDV, PDV, percentiles, CSV input | `netcalc jitter rfc3550 --send 0 20 40 --recv 5 26 44` |
| `loss` | loss ratio, multi-hop loss, burst/duplicate/reorder analysis | `netcalc loss seq 1 2 3 6 7 7 5 8 12` |
| `throughput` | BDP, window-limited throughput, window scaling, transfer time | `netcalc throughput bdp --rate 10G --rtt 80ms` |
| `tcp` | Mathis and Padhye TCP throughput models, max tolerable loss | `netcalc tcp mathis --rtt 50ms --loss 1e-4` |
| `availability` | availability from MTBF/MTTR, series, parallel and k-of-n systems, nines and downtime per year | `netcalc availability parallel 0.99 0.99` |
| `mos` | E-model R-factor and MOS from delay, jitter and loss per codec, delay budget for a target MOS | `netcalc mos score --delay 80ms --jitter 10ms --loss 0.5` |

### CCNA / CCNP (`netcalc.ccna`)

| tool | what it answers | example |
|---|---|---|
| `subnet` | network/broadcast/host range, mask and wildcard, class, prefix for N hosts, split (IPv4 and IPv6) | `netcalc subnet split 10.0.0.0/22 --prefix 24` |
| `vlsm` | VLSM plan for named segments | `netcalc vlsm 192.168.1.0/24 SALES=100 ENG=50 HR=20` |
| `wildcard` | mask/wildcard conversion, ACL matching (non-contiguous too), range to ACL entries | `netcalc wildcard match 10.1.1.0 0.0.254.255 10.1.7.9` |
| `summarize` | exact aggregate and single summary route, with over-coverage warning | `netcalc summarize 172.16.0.0/24 172.16.1.0/24` |
| `ospf` | interface cost, path cost, reference bandwidth table | `netcalc ospf table --ref 400G` |
| `eigrp` | classic composite metric with K values, feasibility condition, variance | `netcalc eigrp metric --bw-kbps 100000 --delay-us 100` |
| `stp` | 802.1D timers from diameter, short/long port costs, root election | `netcalc stp timers --diameter 4` |
| `qos` | M/M/1 queueing delay, CBWFQ shares, shaper Tc and policer Bc | `netcalc qos mm1 --rate 1G --load 0.8` |

### Protocols (`netcalc.protocols`)

| tool | what it answers | example |
|---|---|---|
| `overhead` | header bytes, wire efficiency, goodput and pps for Ethernet/IP/TCP/UDP/VXLAN/RoCEv2 stacks | `netcalc overhead goodput --payload 4096 --stack roce --rate 400G` |
| `mtu` | TCP MSS, overlay underlay MTU (VXLAN, GRE, IPsec, ...), RoCE path MTU | `netcalc mtu overlay --inner-mtu 1500 vxlan` |
| `ipv6` | EUI-64 interface ID, SLAAC and link-local addresses, solicited-node group and MAC, subnet counts | `netcalc ipv6 eui64 00:1b:44:11:3a:b7 --prefix 2001:db8:1:1::/64` |
| `ipsec` | ESP packet size and overhead (tunnel/transport, NAT-T, GCM/CBC), largest inner MTU and MSS clamp | `netcalc ipsec mtu --path-mtu 1500 --nat-t` |
| `nat` | CGNAT subscribers per address, public pool size, port block size from peak sessions, deterministic NAT mapping | `netcalc nat pool --subscribers 100000 --ports 1024` |

### AI fabric (`netcalc.aifabric`)

| tool | what it answers | example |
|---|---|---|
| `loadbalance` | ECMP collision probability, worst-path load for flow hashing vs packet spraying | `netcalc loadbalance imbalance --flows 64 --paths 64 --spray 64` |
| `retransmit` | go-back-N vs selective retransmission goodput, message tail time under loss | `netcalc retransmit compare --loss 1e-4 --rate 400G` |
| `mrc` | multipath reliable connection: entropy values to cover paths, failover capacity, reorder buffer | `netcalc mrc entropy --paths 64` |
| `roce` | PFC headroom, pause quanta, ECN marking curve, DCQCN rate trace | `netcalc roce headroom --rate 400G --cable 100m` |
| `buffer` | incast peak queue, absorb time, shared-buffer dynamic thresholds | `netcalc buffer dt --buffer 64MB --queues 8` |
| `collectives` | NCCL algbw/busbw, ring all-reduce time (alpha-beta model) | `netcalc collectives busbw --size 1GB --time 25ms --ranks 64` |
| `parallelism` | data/tensor/pipeline-parallel bytes per step, pipeline bubble, exposed communication time | `netcalc parallelism dp --params 70e9 --ranks 64 --bw 400G` |
| `algorithms` | ring vs tree vs halving-doubling all-reduce, ring/tree crossover size, hierarchical (scale-up + scale-out) all-reduce | `netcalc algorithms compare --size 64MB --ranks 512 --bw 400G --alpha 5us` |
| `checkpoint` | checkpoint size and write time, job MTBF, interruption probability, Young/Daly interval and wasted time | `netcalc checkpoint interval --write 60s --gpus 16384 --mtbf 50000` |
| `topology` | two- and three-tier Clos limits, leaf-spine plan with oversubscription, rail-optimised leaves, optics, bisection | `netcalc topology plan --hosts 2048 --radix 64` |
| `inference` | KV-cache bytes per token and per context, prefill-to-decode transfer time, memory-bound decode rate, max batch | `netcalc inference kv --layers 80 --kv-heads 8 --head-dim 128 --tokens 32768` |

### Optics and DWDM (`netcalc.optics`)

| tool | what it answers | example |
|---|---|---|
| `dwdm` | ITU-T grid frequency/wavelength, channel lookup, band plans, flexgrid slot width | `netcalc dwdm plan --band C --spacing 100` |
| `budget` | span loss, power budget and margin, receiver overload, attenuation-limited reach | `netcalc budget margin --km 40 --tx -1 --sens -18` |
| `dispersion` | accumulated CD, CD- and PMD-limited reach for NRZ, compensation needed | `netcalc dispersion reach --rate 10G` |
| `coherent` | line and net rate from baud, modulation and FEC, baud for a target rate, spectral efficiency, capacity per fibre | `netcalc coherent rate --baud 59.84 --mod 16qam --fec 0.148` |
| `amplifier` | per-channel power from total output, spans and inline amplifiers, Friis cascaded noise figure | `netcalc amplifier friis 20:5 15:6 10:8` |

### Wireless (`netcalc.wireless`)

| tool | what it answers | example |
|---|---|---|
| `rf` | free-space path loss, EIRP, received level and fade margin, Fresnel zone, earth bulge, radio horizon | `netcalc rf link --tx 20 --tx-gain 23 --rx-gain 23 --km 10 --mhz 5800 --sens -75` |
| `capacity` | thermal noise floor, Shannon capacity, SNR needed for a rate, Eb/N0, SINR | `netcalc capacity shannon --bw 80M --snr 30` |
| `wifi` | 802.11n/ac/ax PHY rate per MCS, width, streams and guard interval, channel frequencies, airtime | `netcalc wifi rate --std ax --mcs 11 --width 80 --nss 2` |

### Queueing theory (`netcalc.queueing`)

| tool | what it answers | example |
|---|---|---|
| `littles` | Little's law for any unknown, utilisation law, buffer bytes from queueing delay | `netcalc littles buffer --rate 400G --delay 10us` |
| `erlang` | Erlang B blocking, circuits for a blocking target, Erlang C wait probability, mean wait and service level | `netcalc erlang size --traffic 10 --blocking 0.01` |
| `mg1` | Pollaczek-Khinchine and M/D/1 wait, Kingman G/G/1 approximation, packet-size mix moments | `netcalc mg1 mix --rate 10G --load 0.7 64:7 576:4 1500:1` |
| `mm1k` | M/M/1/K state probabilities, loss, carried load, delay, buffer size for a loss target | `netcalc mm1k size --load 0.9 --loss 1e-6` |

### Traffic management / QoS (`netcalc.traffic`)

| tool | what it answers | example |
|---|---|---|
| `dscp` | DSCP names and numbers, ToS byte encode/decode, IP precedence, AF drop precedence, RFC 4594 classes | `netcalc dscp lookup AF41` |
| `marker` | RFC 2697 srTCM and RFC 2698 trTCM colouring of a packet trace, bytes per colour, conforming burst | `netcalc marker srtcm --cir 1M --cbs 3000 --ebs 3000 0:1500 0:1500 0:1500` |
| `wred` | RED/WRED drop probability, count-spaced drops, EWMA average queue, per-AF profiles | `netcalc wred prob --avg 35 --min 20 --max 40` |
| `scheduler` | weighted max-min fair shares, DWRR quanta and round time, strict-priority residual and blocking | `netcalc scheduler fair --capacity 10G A=2G B=6G C=6G` |

### Routing protocols (`netcalc.routing`)

| tool | what it answers | example |
|---|---|---|
| `bgp` | BGP best-path selection with the deciding step, full-mesh vs route-reflector sessions, asdot, private ASNs | `netcalc bgp best "A:lp=200,path=65001 65002" B:path=65003` |
| `spf` | Dijkstra shortest paths with ECMP next hops, all equal-cost paths, loop-free alternates (link/node protecting) | `netcalc spf lfa --src S --dst D S-E:10 E-D:10 S-N:10 N-D:15` |
| `bfd` | negotiated BFD intervals, detection time at each end, packet load, false session-downs from random loss | `netcalc bfd flaps --interval 10ms --mult 3 --loss 1e-3` |
| `isis` | decode NETs, system ID from a loopback, wide/narrow metric from bandwidth, LSP refresh load | `netcalc isis sysid 192.168.1.1 --area 49.0001` |
| `fhrp` | VRRPv3 skew and master down interval, HSRP timer check, VRRP/HSRP virtual MACs, host failover time | `netcalc fhrp vrrp --interval 1 --priority 100` |
| `mpls` | label stack overhead and core MTU, usable label space, RSVP-TE full-mesh LSPs, SR MSD check, label entry encode/decode | `netcalc mpls stack --labels 3 --payload-mtu 1500` |
| `evpn` | EVPN type-2/3/5 route counts, ingress replication load for BUM traffic, VNI and local VLAN limits | `netcalc evpn routes --vteps 64 --vnis 500 --hosts 40000` |
| `convergence` | IGP convergence budget (detect, flood, SPF, FIB), effect of prefix-independent convergence, traffic lost | `netcalc convergence budget --detect 150ms --prefixes 20000 --per-prefix 20us` |

## Examples

The `examples/` folder combines several tools into small reports:

| script | what it does |
|---|---|
| `examples/link_report.py --pre-ber 3e-7` | Q-factor, KP4 post-FEC BER, FEC margin and verdict for a PAM4 link |
| `examples/campus_plan.py 10.20.0.0/22 USERS=400 VOICE=200` | VLSM plan with ACL wildcards, the summary route and OSPF uplink costs |
| `examples/ai_fabric_sizing.py --gpus 512 --rate 400G` | ECMP vs spraying efficiency, PFC headroom, reorder buffer and all-reduce time |

`examples/sample_delays.csv` is a sample input for `netcalc jitter file examples/sample_delays.csv`.

## Repository layout

```
netcalc-toolkit/
├── netcalc/
│   ├── __main__.py        # `python -m netcalc` / `netcalc` dispatcher
│   ├── units.py           # parse "100G", "9KB", "10ms"; dB helpers
│   ├── layer1/            # ber, qfactor, fec, ser, osnr
│   ├── perf/              # latency, jitter, loss, throughput, tcp
│   ├── ccna/              # subnet, vlsm, wildcard, summarize, ospf, eigrp, stp, qos
│   ├── protocols/         # overhead, mtu
│   └── aifabric/          # loadbalance, retransmit, mrc, roce, buffer, collectives
├── examples/              # multi-tool reports built on the library
├── tests/                 # unittest suite, one file per module
├── README.md
├── TECHNOLOGY.md          # the concepts and formulas behind each tool
└── pyproject.toml
```

## Accuracy notes

These are engineering estimates, not vendor sign-off tools. FEC math assumes
independent bit errors (real links have bursts and error propagation from
DFE), PFC headroom uses a generic response time, and the TCP models describe
loss-based congestion control. Each docstring states its assumptions; check
vendor documentation before configuring production hardware.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a calculator, and
[CHANGELOG.md](CHANGELOG.md) for what is included.

## About the commit history

The commit history of this repository was intentionally backdated so that
the GitHub contribution graph spells **VIJAY**. The code was written in one
session (with help from Claude, an AI assistant) and then committed
incrementally, one function, test or doc section at a time, with
`GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` set to the dates that draw the letters.
The dates show when each piece was committed for the graph, not when it was
written.

## License

MIT, see [LICENSE](LICENSE).
