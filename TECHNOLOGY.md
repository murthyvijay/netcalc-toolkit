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
