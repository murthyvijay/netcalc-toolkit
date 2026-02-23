"""Reed-Solomon FEC: correction capability, post-FEC BER, threshold and margin.

Ethernet PHYs from 25G upward rely on Reed-Solomon forward error correction.
A code RS(n, k) over m-bit symbols carries k data symbols and n - k parity
symbols per codeword and corrects up to ``t = (n - k) // 2`` errored
symbols anywhere in the codeword.

Common presets:

=========  ===============  ===  ==================================
name       code             t    used by
=========  ===============  ===  ==================================
kr4        RS(528,514) m=10  7   25GBASE-R, 100GBASE-KR4/CR4/SR4
kp4        RS(544,514) m=10 15   PAM4 lanes: 200G/400G/800G Ethernet
=========  ===============  ===  ==================================

Assuming independent bit errors at the FEC input (no bursts), this module
estimates the codeword error ratio and post-FEC BER, finds the pre-FEC BER
threshold for a target post-FEC BER, and reports the margin of a measured
link against that threshold.

Usage::

    python -m netcalc.layer1.fec info --code kp4
    python -m netcalc.layer1.fec post --code kp4 --pre-ber 2e-4
    python -m netcalc.layer1.fec threshold --code kp4 --target 1e-13
    python -m netcalc.layer1.fec margin --code kp4 --pre-ber 1e-6
"""

import argparse
import math
from collections import namedtuple

from netcalc.layer1.qfactor import ber_to_q

RSCode = namedtuple("RSCode", "n k m")

PRESETS = {
    "kr4": RSCode(528, 514, 10),
    "kp4": RSCode(544, 514, 10),
}


def get_code(name_or_code):
    """Return an :class:`RSCode` from a preset name or ``"n,k,m"`` string."""
    if isinstance(name_or_code, RSCode):
        return name_or_code
    key = str(name_or_code).lower()
    if key in PRESETS:
        return PRESETS[key]
    n, k, m = (int(x) for x in key.split(","))
    return RSCode(n, k, m)


def correctable_symbols(code):
    """Number of symbol errors ``t`` the code can correct per codeword."""
    return (code.n - code.k) // 2


def code_rate(code):
    """Fraction of transmitted symbols that carry data (k / n)."""
    return code.k / code.n


def overhead_pct(code):
    """Parity overhead relative to the payload, in percent."""
    return (code.n - code.k) / code.k * 100


def max_burst_bits(code):
    """Longest bit burst that is always correctable.

    A burst can straddle symbol boundaries, so ``t`` symbols guarantee
    ``(t - 1) * m + 1`` contiguous errored bits.
    """
    return (correctable_symbols(code) - 1) * code.m + 1


def symbol_error_prob(pre_ber, m):
    """Probability that an m-bit symbol contains at least one bit error."""
    return -math.expm1(m * math.log1p(-pre_ber))


def _binom_term(n, i, p):
    log = (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
           + i * math.log(p) + (n - i) * math.log1p(-p))
    return math.exp(log)


def codeword_error_ratio(pre_ber, code):
    """Probability that a codeword has more than t errored symbols (uncorrectable)."""
    code = get_code(code)
    if pre_ber <= 0:
        return 0.0
    p = symbol_error_prob(pre_ber, code.m)
    t = correctable_symbols(code)
    return sum(_binom_term(code.n, i, p) for i in range(t + 1, code.n + 1))


def post_fec_ber(pre_ber, code):
    """Estimated BER after decoding.

    Uncorrectable codewords pass their errored symbols through; the output
    symbol error rate is ``sum(i/n * P(i errors))`` for i > t, and a wrong
    m-bit symbol has on average ``2^(m-1) / (2^m - 1)`` of its bits flipped.
    """
    code = get_code(code)
    if pre_ber <= 0:
        return 0.0
    p = symbol_error_prob(pre_ber, code.m)
    t = correctable_symbols(code)
    ser_out = sum(i / code.n * _binom_term(code.n, i, p) for i in range(t + 1, code.n + 1))
    return ser_out * 2 ** (code.m - 1) / (2 ** code.m - 1)


def pre_fec_threshold(code, target_post_ber=1e-13):
    """Highest pre-FEC BER that still meets ``target_post_ber`` (log bisection)."""
    code = get_code(code)
    lo, hi = -15.0, math.log10(0.4)
    for _ in range(100):
        mid = (lo + hi) / 2
        if post_fec_ber(10 ** mid, code) > target_post_ber:
            hi = mid
        else:
            lo = mid
    return 10 ** lo


def fec_margin(measured_pre_ber, code, target_post_ber=1e-13):
    """Margin of a measured link against the FEC threshold.

    Returns a dict with the threshold, the margin in decades of BER
    (``log10(threshold / measured)``) and the margin expressed as Q in dB.
    """
    threshold = pre_fec_threshold(code, target_post_ber)
    return {
        "threshold": threshold,
        "decades": math.log10(threshold / measured_pre_ber),
        "q_margin_db": 20 * math.log10(ber_to_q(measured_pre_ber) / ber_to_q(threshold)),
        "post_fec_ber": post_fec_ber(measured_pre_ber, code),
        "pass": measured_pre_ber <= threshold,
    }
