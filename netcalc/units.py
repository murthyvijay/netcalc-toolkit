"""Unit parsing and formatting helpers shared by every netcalc tool.

Network math constantly mixes units: link rates in Gbps, buffers in KB or
MiB, delays in microseconds. These helpers let every CLI accept friendly
strings such as ``"100G"``, ``"9KB"`` or ``"2.5us"`` and turn them into plain
SI base units (bits per second, bytes, seconds).

Decimal prefixes (k, M, G, T) are powers of 1000; binary prefixes
(Ki, Mi, Gi, Ti) are powers of 1024.
"""

import math
import re

SPEED_OF_LIGHT_M_S = 299_792_458.0
FIBER_REFRACTIVE_INDEX = 1.468

_DECIMAL = {"": 1, "k": 1e3, "K": 1e3, "m": 1e6, "M": 1e6, "g": 1e9, "G": 1e9, "t": 1e12, "T": 1e12}
_BINARY = {"Ki": 1024, "Mi": 1024 ** 2, "Gi": 1024 ** 3, "Ti": 1024 ** 4}
_TIME = {"s": 1.0, "ms": 1e-3, "us": 1e-6, "µs": 1e-6, "ns": 1e-9, "ps": 1e-12}

_NUM = r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)"
