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
