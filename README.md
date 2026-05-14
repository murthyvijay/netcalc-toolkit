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
