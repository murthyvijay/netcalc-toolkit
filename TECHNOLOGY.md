# Technology guide

This document explains the networking concepts behind each netcalc tool and
the formulas it uses. Notation: `R` = line rate (bits/s), `RTT` = round-trip
time, `p` = probability (loss or error), `log` = log10 unless noted.

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
