# Technology guide

This document explains the networking concepts behind each netcalc tool and
the formulas it uses. Notation: `R` = line rate (bits/s), `RTT` = round-trip
time, `p` = probability (loss or error), `log` = log10 unless noted.

- [1. Layer 1: errors, FEC and optical noise](#1-layer-1-errors-fec-and-optical-noise)
- [2. Latency, jitter, loss and throughput](#2-latency-jitter-loss-and-throughput)
- [3. CCNA / CCNP calculations](#3-ccna--ccnp-calculations)
- [4. Protocol overhead and MTU](#4-protocol-overhead-and-mtu)
- [5. AI/ML fabrics](#5-aiml-fabrics)
- [6. Optics and DWDM](#6-optics-and-dwdm)
- [7. Wireless](#7-wireless)
- [8. Queueing theory](#8-queueing-theory)
- [References](#references)

---

## 1. Layer 1: errors, FEC and optical noise

### Bit error ratio (`ber`)

`BER = errored bits / total bits`. Because good links have BER around
1e-12 or better, you never observe "the" BER directly; you observe a handful
of errors (often zero) and make a statistical claim. Errors are modelled as
Poisson with mean `N * BER` for N bits. The confidence that the true BER is
below a target is

```
CL = 1 - sum_{k=0}^{E} (N*BER)^k e^(-N*BER) / k!
```

With zero errors this simplifies to `N = -ln(1 - CL) / BER`, the "rule of
three": about `3 / BER` bits for 95 % confidence. At 100 Gb/s, proving
BER < 1e-12 takes about 30 seconds; proving 1e-15 takes over 8 hours, which
is why post-FEC BER is estimated rather than measured.

### Q-factor (`qfactor`)

For a binary signal with Gaussian noise on the one and zero levels
(`mu1, sigma1`, `mu0, sigma0`), the Q-factor is
`Q = (mu1 - mu0) / (sigma1 + sigma0)` and

```
BER = 0.5 * erfc(Q / sqrt(2))
```

Q = 6 gives about 1e-9, Q = 7 about 1e-12. Q in dB is `20 log Q` because Q is
an amplitude ratio; Q-margin in dB is how optical engineers express
headroom.

### Symbol error rate (`ser`)

Multi-level signalling carries `log2 M` bits per symbol. In additive white
Gaussian noise with SNR per symbol `Es/N0`:

```
PAM-M:  SER = 2 (1 - 1/M) Q( sqrt( 3 SNR / (M^2 - 1) ) )
QAM-M:  SER = 1 - (1 - 2 (1 - 1/sqrt M) Q( sqrt( 3 SNR / (M - 1) ) ))^2
```

where `Q(x)` is the Gaussian tail. PAM4 (used by 50G/100G/200G-per-lane
Ethernet) needs about 7 dB more average SNR than NRZ for the same SER, or
9.5 dB at equal peak amplitude, because each of its three eyes is a third of
the height. With Gray coding a symbol error almost always
flips one bit, so `BER ~ SER / log2 M`.

### Reed-Solomon FEC (`fec`)

`RS(n, k)` over m-bit symbols sends `k` data symbols plus `n - k` parity
symbols and corrects any `t = (n - k) / 2` errored symbols per codeword.

| code | n, k, m | t | overhead | used in |
|---|---|---|---|---|
| "KR4" | 528, 514, 10 | 7 | 2.7 % | 25G, 100G NRZ (Clause 91) |
| "KP4" | 544, 514, 10 | 15 | 5.8 % | PAM4: 200G/400G/800G |

**Pre-FEC vs post-FEC BER.** With independent bit errors at rate `p_b`, a
10-bit symbol is wrong with `p_s = 1 - (1 - p_b)^m`. A codeword fails when
more than `t` of its `n` symbols are wrong:

```
P_cw = sum_{i=t+1}^{n} C(n,i) p_s^i (1 - p_s)^(n-i)
```

Failed codewords pass their errors through, so the output symbol error rate
is `sum (i/n) C(n,i) p_s^i (1-p_s)^(n-i)` and the post-FEC BER is that times
`2^(m-1) / (2^m - 1)` (average fraction of bits wrong in a wrong symbol).

**Threshold and margin.** The pre-FEC threshold is the input BER at which the
post-FEC BER hits the target (netcalc defaults to 1e-13). KP4 tolerates
roughly 2e-4 to 3e-4 pre-FEC. FEC margin is how far the measured link sits
below that threshold, either in decades (`log(threshold / measured)`) or as
Q-margin in dB (`20 log(Q_measured / Q_threshold)`).

**Coding gain.** Net coding gain compares the Q needed with and without FEC
at the same output BER and charges for the rate overhead:

```
NCG = 20 log(Q_target) - 20 log(Q_threshold) + 10 log(k / n)
```

Real links have burst errors (DFE error propagation, for example), which
these independent-error formulas underestimate; interleaving across lanes
in 400G/800G PCS exists partly to spread bursts across codewords.

### OSNR and SNR (`osnr`)

OSNR is measured in a 0.1 nm reference bandwidth (`Bref = c * dlambda /
lambda^2`, about 12.5 GHz at 1550 nm). Electrical SNR of a coherent receiver
relates to it through the symbol rate `Rs` and polarisations `p`:

```
OSNR = (p * Rs / (2 * Bref)) * SNR
```

so doubling the baud rate costs 3 dB of SNR at the same OSNR. Each EDFA in a
chain adds ASE noise; with input power `P_in` and noise figure `NF`:

```
OSNR_dB = 58 + P_in(dBm) - NF(dB) - 10 log(N spans)
1 / OSNR_total = sum 1 / OSNR_i          (linear)
```

---

## 2. Latency, jitter, loss and throughput

### Latency (`latency`)

| component | formula | example |
|---|---|---|
| serialization | `bits / R` | 1500 B at 10G = 1.2 us; 9000 B at 400G = 180 ns |
| propagation | `distance * n / c` | fibre n = 1.468, about 4.9 us/km or 204 km/ms |
| processing | per device | 300 ns to a few us for switches |
| queueing | depends on load | see QoS below |

Store-and-forward devices pay serialization at every hop; cut-through
switches start forwarding after the header, so serialization is paid once.

### Jitter (`jitter`)

RFC 3550 defines interarrival jitter from sender timestamps `S` and receive
times `R`:

```
D(i-1, i) = (R_i - R_{i-1}) - (S_i - S_{i-1})
J = J + (|D| - J) / 16
```

The difference of differences cancels any constant clock offset between the
hosts, and the 1/16 gain makes J a smoothed mean deviation. IPDV (RFC 3393)
keeps the raw sequence of consecutive delay differences; PDV (RFC 5481)
measures each delay against the minimum and is the better input for sizing
de-jitter buffers (use a high percentile).

### Packet loss (`loss`)

`loss = (sent - received) / sent`. Over independent hops,
`loss_e2e = 1 - prod (1 - p_i)`. The probability that a message of N packets
loses at least one is `1 - (1 - p)^N`: at p = 1e-5 a 64 MB message in 4 KB
packets (16 384 packets) has a 15 % chance of needing recovery. The `seq`
analyser also counts bursts, duplicates and reordering, because the burst
structure matters as much as the average.

### Throughput and BDP (`throughput`)

A window-based sender can have at most one window per RTT in flight:
`throughput <= W / RTT`. Filling a link needs `W >= BDP = R * RTT`. A 64 KB
window over 30 ms RTT caps one flow at 17.5 Mb/s; 10G over 80 ms needs a
100 MB window, which TCP can only advertise with window scaling (RFC 7323,
shift count up to 14).

### TCP models (`tcp`)

Mathis et al. (1997) for loss-based congestion avoidance:

```
throughput = (MSS / RTT) * sqrt(3/2) / sqrt(p)
```

Padhye et al. (1998) add retransmission timeouts, which dominate when loss
is high:

```
B = MSS / ( RTT sqrt(2bp/3) + RTO min(1, 3 sqrt(3bp/8)) p (1 + 32 p^2) )
```

Both show why long-RTT paths are so sensitive to loss: throughput falls as
`1 / (RTT * sqrt(p))`.

---

## 3. CCNA / CCNP calculations

### Subnetting and VLSM (`subnet`, `vlsm`)

For prefix length `L` in IPv4 there are `2^(32-L)` addresses and
`2^(32-L) - 2` usable hosts (network and broadcast reserved), except /31
point-to-point links (RFC 3021, 2 hosts) and /32 host routes. The prefix that
fits H hosts is `32 - ceil(log2(H + 2))`. VLSM allocates the largest segment
first and aligns each subnet on a multiple of its size, which guarantees no
overlap and minimal waste.

### Wildcard masks (`wildcard`)

A wildcard is the inverse of a mask: `0` = must match, `1` = ignore. An
address matches an ACL entry when `(entry & ~wildcard) == (addr & ~wildcard)`.
Wildcards need not be contiguous: `10.1.1.0 0.0.254.255` matches every odd
third octet. An entry with `k` one-bits matches `2^k` addresses.

### Summarization (`summarize`)

A single summary is the longest prefix shared by the lowest and highest
address: `prefix = 32 - bit_length(low XOR high)`. If the component routes do
not fill it, the summary also attracts traffic for addresses you do not have
(a black-hole risk), which the tool reports.

### OSPF cost (`ospf`)

`cost = max(1, floor(reference_bw / interface_bw))`, path cost is the sum of
outgoing interface costs. The 100 Mb/s default makes every modern link cost 1,
so set `auto-cost reference-bandwidth` above your fastest link on every
router.

### EIGRP metric (`eigrp`)

```
BW    = 10^7 / min bandwidth (kbps)
DELAY = sum delay (us) / 10
metric = 256 * (K1 BW + K2 BW / (256 - load) + K3 DELAY) [* K5 / (rel + K4)]
```

Default K values (1, 0, 1, 0, 0) give `256 * (BW + DELAY)`. A neighbour is a
feasible successor (loop-free backup) when its reported distance is strictly
less than the current feasible distance. `variance V` allows unequal-cost
paths with metric up to `V *` the best.

### Spanning Tree (`stp`)

802.1D ties timers to the network diameter `d` and hello time `h`:
`max_age = 4h + 2d - 2`, `forward_delay = (4h + 3d) / 2`. Defaults (h = 2,
d = 7) give 20 s and 15 s; reconvergence after an indirect failure can take
`max_age + 2 * forward_delay` = 50 s, which RSTP replaces with
proposal/agreement handshakes. Port cost is 802.1D short (4 for 1G, 2 for
10G) or 802.1t long (`20 Tb/s / bandwidth`). The root bridge has the lowest
bridge ID: priority (a multiple of 4096 plus the VLAN with extended system
ID), then MAC.

### QoS and queueing (`qos`)

For an M/M/1 queue with utilisation `rho`, mean waiting time is
`rho / (mu - lambda)` and mean queue length `rho^2 / (1 - rho)`. At 50 %
load the queue holds 0.5 packets on average; at 90 % it holds 8.1. CBWFQ
guarantees each class its configured share under congestion. A token-bucket
shaper refills every `Tc = Bc / CIR`; Cisco's policer guideline is
`Bc = CIR / 8 * 1.5 s` bytes.

---

## 4. Protocol overhead and MTU

### Header overhead and goodput (`overhead`)

On the wire each Ethernet frame adds an 8-byte preamble/SFD and a 12-byte
inter-frame gap to its 14-byte header and 4-byte FCS. Goodput is

```
goodput = R * payload / (payload + headers + 20)
```

| stack | headers (B) | efficiency at full size |
|---|---|---|
| Ethernet/IPv4/TCP, 1460 B payload | 58 | 94.9 % |
| VXLAN (IPv4 underlay) carrying TCP | 108 | about 92 % at 1500 B inner MTU |
| RoCEv2 (Eth/IPv4/UDP/BTH/ICRC), 4096 B | 62 | 98.0 % |

Minimum frames are 64 bytes (84 on the wire), so 10GbE tops out at 14.88
Mpps; this is the figure to size packet-rate limited devices against.

### MTU and MSS (`mtu`)

`MSS = MTU - IP header (20 or 40) - TCP header (20) - options`. Overlays
consume underlay MTU: VXLAN over IPv4 adds 50 bytes (outer Ethernet 14,
IPv4 20, UDP 8, VXLAN 8), so a 1500-byte tenant MTU needs at least 1550 in
the underlay, and data-centre fabrics usually run 9216. RoCEv2 picks its path
MTU from 256 to 4096 bytes; with a 1500-byte Ethernet MTU only 1024 fits,
which is why RDMA fabrics run jumbo frames.

---

## 5. AI/ML fabrics

Distributed training synchronises gradients with collectives (all-reduce,
all-gather, reduce-scatter, all-to-all) that move very large messages between
every GPU, in lock step. The job advances at the speed of the slowest flow,
so tail behaviour (worst link, worst loss event) matters more than averages.

### Load balancing: ECMP vs packet spraying (`loadbalance`)

ECMP hashes each flow's 5-tuple to one path. With few, large flows, hash
collisions are almost certain: placing F flows on P paths has collision
probability `1 - P! / ((P - F)! P^F)` (the birthday problem), and on average
`P (1 - 1/P)^F` paths stay idle. With 64 flows on 64 paths the busiest path
typically carries about 4x its fair share, so a synchronous job sees roughly
25 % of fabric bandwidth.

Two fixes appear in practice:

* **More entropy per connection.** Split each connection over several queue
  pairs or sub-flows with different UDP source ports (Meta describes using
  multiple QPs per GPU pair to improve ECMP spread). `--spray N` models N
  independently hashed sub-flows per flow.
* **Packet spraying.** Choose a path per packet, as Ultra Ethernet's transport
  does. Load becomes nearly even, at the cost of out-of-order arrival, which
  the transport must tolerate.

### Ultra Ethernet and loss recovery (`retransmit`)

The Ultra Ethernet Consortium (UEC) defines an Ethernet stack for AI and HPC.
Its transport (UET) is designed around multipath packet spraying: each packet
carries an entropy value used for path selection, delivery can be unordered,
loss is repaired by selective retransmission, and congestion control combines
sender-side signals (ECN, delay) with receiver-side credit. It does not
depend on a lossless (PFC) fabric.

Why selective retransmission matters: classic RoCE NICs use **go-back-N**,
resending everything after a lost packet. With `W` packets in flight,

```
go-back-N efficiency   = (1 - p) / (1 - p + p W)
selective efficiency   = 1 - p
```

At 400 Gb/s and 10 us RTT, W is about 123 packets of 4 KB; at p = 1e-4
go-back-N loses about 1.2 % of goodput while selective repeat loses 0.01 %.
Spraying also creates reordering that go-back-N would treat as loss, so
spraying and selective repair go together. For tail latency, the expected
completion time of a message of N packets is
`base + (1 - (1 - p)^N) * recovery_time`.

### Multipath reliable connection (`mrc`)

A multipath reliable connection keeps the semantics of one reliable RDMA
connection while spreading its packets over many paths by varying the
entropy field. Sizing questions:

* **Entropy coverage.** Random entropy values hit paths like coupons: touching
  all P paths takes `P * H(P)` values on average (`H` = harmonic number,
  about 304 for 64 paths). The probability that V values cover all paths is
  `sum_k (-1)^k C(P,k) (1 - k/P)^V`.
* **Failover.** Removing f failed paths from the spray set leaves
  `(P - f) / P` of capacity, instead of stalling the flows hashed onto them.
* **Reorder buffer.** The receiver must hold data for the delay skew between
  the fastest and slowest path: `buffer = R * skew (+ one MTU)`. 800 Gb/s with
  4 us of skew needs about 400 KB per connection.

### RoCEv2, PFC, ECN and DCQCN (`roce`)

RoCEv2 carries InfiniBand transport (BTH) over UDP port 4791. Because its NIC
transport traditionally uses go-back-N, the fabric is made lossless with
**Priority Flow Control** (802.1Qbb): a congested queue pauses the upstream
port for one traffic class.

**PFC headroom.** After XOFF is triggered, data keeps arriving for a round
trip on the cable plus reaction time. Per priority and port:

```
headroom = 2 * cable_delay * R / 8 + 2 * MTU + response_time * R / 8 + 64
```

At 400 Gb/s on 100 m of fibre this is roughly 100 KB, which is why deep
headroom pools and short cables matter. A pause of `q` quanta lasts
`q * 512 / R` seconds.

**ECN and DCQCN.** Switches mark ECN between thresholds Kmin and Kmax with a
RED-style probability (0 below Kmin, linear to Pmax, 1 above Kmax). The
receiver NIC returns Congestion Notification Packets; DCQCN cuts the rate
`Rc <- Rc (1 - alpha/2)` with `alpha <- (1 - g) alpha + g`, then recovers
toward the pre-cut target rate in fast-recovery and additive-increase stages.

**Meta's RoCE experience.** Meta's SIGCOMM 2024 paper on RDMA over Ethernet
for training at scale reports running RoCEv2 with PFC on dedicated backend
fabrics, handling ECMP imbalance with more queue pairs per connection and
traffic engineering, and finding that receiver-driven admission in the
collective library, rather than DCQCN tuning, was the effective way to
control congestion in their setting. The `loadbalance --spray` and `buffer`
tools model the first and last of those trade-offs.

### Switch buffers (`buffer`)

**Incast.** N senders bursting B bytes each at line rate into one port build
a queue of about `N * B - drained` (with equal rates, `(N - 1) * B`).
A buffer absorbs `N` senders for `buffer * 8 / ((N * R_sender) - R_port)`
seconds.

**Dynamic thresholds.** Shared-buffer switches cap each queue at
`alpha * free buffer`. With n equally congested queues the per-queue limit
settles at `alpha * B / (1 + alpha * n)` and `B / (1 + alpha * n)` stays free
for new bursts, which is the trade-off alpha tunes.

### Collectives (`collectives`)

Benchmarks such as nccl-tests report `algbw = size / time` and
`busbw = algbw * factor`, where the factor (`2(n-1)/n` for all-reduce,
`(n-1)/n` for all-gather, reduce-scatter and all-to-all) converts to per-link
load so it can be compared with link speed. The alpha-beta model of a ring
all-reduce is

```
T = 2 (n - 1) alpha + 2 (n - 1) / n * S / B
```

The first term (latency) grows with ranks, which is why large jobs switch to
tree or hierarchical algorithms for small messages.

---

## 6. Optics and DWDM

Long-haul and metro links multiplex many wavelengths on one fibre (DWDM),
amplify them every 60-100 km with EDFAs, and today mostly use coherent
transceivers whose DSP undoes dispersion. Planning one is a chain of budgets:
power (is there enough light?), noise (is OSNR high enough?), dispersion (can
the receiver undo the pulse spreading?) and spectrum (how many channels fit?).

### DWDM grid (`dwdm`)

ITU-T G.694.1 anchors the fixed grid at 193.1 THz: channel n sits at
`193.1 THz + n * spacing` with 100, 50, 25 or 12.5 GHz spacing, and
`lambda = c / f` (193.1 THz is 1552.52 nm). At 1550 nm, 100 GHz is about
0.8 nm (`dlambda = lambda^2 df / c`). The C band (191.3-196.1 THz) holds 49
channels at 100 GHz or 97 at 50 GHz.

Flexgrid replaces fixed channels with slots centred on a 6.25 GHz grid and
`m * 12.5 GHz` wide. A carrier occupies `baud * (1 + roll-off)`, so a 64 GBd
signal with 0.1 roll-off (70.4 GHz) fits a 75 GHz slot (m = 6) instead of a
100 GHz channel: a third more carriers per fibre.

### Optical power budget (`budget`)

A passive span loses `alpha * L` in the fibre (about 0.35 dB/km at 1310 nm,
0.25 dB/km at 1550 nm) plus about 0.5 dB per connector pair and 0.1 dB per
splice. The link works when

```
P_tx - loss - safety_margin >= receiver sensitivity
```

and the received power is also below the receiver's overload point; short
links with long-reach optics need an attenuator. Solving the budget for L
gives the attenuation-limited reach; splices every few km add
`splice_loss / spacing` to the per-km loss.

### Chromatic dispersion and PMD (`dispersion`)

Chromatic dispersion spreads a pulse by `D * L * dlambda`, with D about 17
ps/(nm km) in standard fibre at 1550 nm. Because a faster signal is both
spectrally wider (`dlambda = lambda^2 B / c`) and has shorter bits, the
uncompensated reach of a direct-detect signal falls with the square of the
bit rate: `L = c / (D lambda^2 B^2)`, about 73 km at 10 Gb/s and under 1 km at
100 Gb/s. That is why 1550 nm direct-detect links above 10G are rare and
coherent receivers, which compensate tens of thousands of ps/nm in the DSP,
took over.

Polarisation mode dispersion is random: the mean differential group delay
grows as `PMD_coef * sqrt(L)`, and NRZ tolerates about 10 % of a bit period.
With a modern 0.1 ps/sqrt(km) fibre that is 10,000 km at 10 Gb/s but only 625
km at 40 Gb/s.

### Coherent line rates (`coherent`)

A dual-polarisation coherent signal carries `baud * bits_per_symbol * 2` bits
per second on the line; FEC (typically 15-25 % overhead) and framing come off
that to give the client rate. 400ZR is 59.84 GBd DP-16QAM: 478.75 Gb/s on the
line for 400GbE. Doubling capacity means doubling baud (wider spectrum) or
adding bits per symbol (needs more OSNR, about 3 dB per extra bit at high
order), which is the reach/rate trade-off of every coherent modem.

Spectral efficiency is net rate over channel spacing: 400G in 75 GHz is 5.3
b/s/Hz, and 64 such channels fill the 4.8 THz C band with 25.6 Tb/s.

### Optical amplifiers (`amplifier`)

An EDFA's total output power is shared by its channels:
`P_ch = P_total - 10 log10(N)`, so 20 dBm across 40 channels is about 4 dBm
each. Inline amplifiers sit every 60-100 km and their gain makes up the
previous span's loss. The OSNR contribution of each amplifier is covered by
`osnr chain`.

Within a multi-stage amplifier (or a receiver chain), noise figures cascade
by the Friis formula in linear units,
`F = F1 + (F2 - 1)/G1 + (F3 - 1)/(G1 G2) + ...`, so the first stage's noise
figure dominates once its gain is high.

---

## 7. Wireless

Radio links follow the same budget logic as optical ones, but the loss
depends on distance and frequency in free space, the noise floor is set by
thermodynamics, and the achievable rate is bounded by Shannon.

### RF link budget (`rf`)

Free-space path loss is `20 log10(d_km) + 20 log10(f_MHz) + 32.44` dB: every
doubling of distance or frequency costs 6 dB. A point-to-point budget is

```
P_rx = P_tx - cable loss + G_tx - FSPL - other losses + G_rx
fade margin = P_rx - receiver sensitivity
```

with 10-20 dB of fade margin typical to ride out rain and multipath.

Line of sight is not enough: the first Fresnel zone, of radius
`17.32 sqrt(d1 d2 / (f_GHz D))` metres, should be at least 60 % clear, and on
long paths the earth itself rises `d1 d2 / (12.74 k)` metres mid-path (k = 4/3
for standard refraction). The radio horizon of an antenna h metres high is
`3.57 sqrt(k h)` km.

### Capacity and noise (`capacity`)

Thermal noise is -174 dBm/Hz at room temperature, so a 20 MHz receiver with
a 7 dB noise figure has a floor of about -94 dBm. Shannon's limit
`C = B log2(1 + SNR)` bounds any modulation and coding: 20 MHz at 30 dB SNR
cannot exceed about 199 Mb/s, and real systems run a few dB short of the
bound. Interference adds to noise in milliwatts, so one strong interferer can
dominate the SINR.

### Wi-Fi PHY rates (`wifi`)

An OFDM Wi-Fi rate is `Nss * Nsd * bits_per_subcarrier * coding_rate / (T_sym + GI)`.
802.11ac uses 3.2 us symbols and 234 data subcarriers in 80 MHz, so MCS 9
(256-QAM 5/6) gives 390 Mb/s per stream with a 0.8 us guard. 802.11ax uses
12.8 us symbols and 980 subcarriers in 80 MHz, and MCS 11 (1024-QAM 5/6)
reaches 600.5 Mb/s per stream; 2 streams at 160 MHz is the familiar
2.4 Gb/s headline.

Those are PHY rates: preambles, contention and acknowledgements mean real
throughput is often 60-70 % of them, and every frame's airtime at a low MCS
is time no one else can use.

---

## 8. Queueing theory

Every buffer, trunk group and server pool is a queue. A few classic results
explain most of what network engineers see: delay rises without bound as
utilisation approaches 1, variability (bursty arrivals, mixed packet sizes)
multiplies queueing delay, and finite buffers turn delay into loss.

---

## References

- RFC 3550 (RTP, interarrival jitter), RFC 3393 (IPDV), RFC 5481 (PDV)
- RFC 7323 (TCP window scaling), RFC 3021 (/31 point-to-point)
- IEEE 802.3 Clause 91 (RS-FEC), IEEE 802.1D / 802.1w / 802.1t, IEEE 802.1Qbb (PFC)
- M. Mathis et al., "The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm", 1997
- J. Padhye et al., "Modeling TCP Throughput: A Simple Model and its Empirical Validation", SIGCOMM 1998
- Y. Zhu et al., "Congestion Control for Large-Scale RDMA Deployments" (DCQCN), SIGCOMM 2015
- A. Gangidi et al., "RDMA over Ethernet for Distributed AI Training at Meta Scale", SIGCOMM 2024
- Ultra Ethernet Consortium, Ultra Ethernet Specification 1.0, 2025
- NVIDIA, nccl-tests performance documentation (algbw and busbw)
