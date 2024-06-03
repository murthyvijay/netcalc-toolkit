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

### AI fabric (`netcalc.aifabric`)

| tool | what it answers | example |
|---|---|---|
| `loadbalance` | ECMP collision probability, worst-path load for flow hashing vs packet spraying | `netcalc loadbalance imbalance --flows 64 --paths 64 --spray 64` |
| `retransmit` | go-back-N vs selective retransmission goodput, message tail time under loss | `netcalc retransmit compare --loss 1e-4 --rate 400G` |
| `mrc` | multipath reliable connection: entropy values to cover paths, failover capacity, reorder buffer | `netcalc mrc entropy --paths 64` |
| `roce` | PFC headroom, pause quanta, ECN marking curve, DCQCN rate trace | `netcalc roce headroom --rate 400G --cable 100m` |
| `buffer` | incast peak queue, absorb time, shared-buffer dynamic thresholds | `netcalc buffer dt --buffer 64MB --queues 8` |
| `collectives` | NCCL algbw/busbw, ring all-reduce time (alpha-beta model) | `netcalc collectives busbw --size 1GB --time 25ms --ranks 64` |

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
