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
