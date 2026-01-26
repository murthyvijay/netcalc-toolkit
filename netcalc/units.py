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


def _split(text):
    m = re.fullmatch(_NUM + r"\s*([A-Za-zµ/]*)", str(text).strip())
    if not m:
        raise ValueError(f"cannot parse quantity: {text!r}")
    return float(m.group(1)), m.group(2)


def parse_rate(text):
    """Parse a data rate into bits per second.

    >>> parse_rate("100G")
    100000000000.0
    >>> parse_rate("25Gbps")
    25000000000.0
    >>> parse_rate("1.5 Mb/s")
    1500000.0
    """
    value, unit = _split(text)
    unit = unit.replace("/s", "").replace("bps", "").replace("bit", "").replace("b", "")
    if unit not in _DECIMAL:
        raise ValueError(f"unknown rate unit in {text!r}")
    return value * _DECIMAL[unit]


def parse_size(text):
    """Parse a size into bytes. ``B`` means bytes, a lone ``b`` means bits.

    >>> parse_size("1500")
    1500.0
    >>> parse_size("9KB")
    9000.0
    >>> parse_size("2MiB")
    2097152.0
    >>> parse_size("8kb")
    1000.0
    """
    value, unit = _split(text)
    if unit.endswith("B"):
        unit, scale = unit[:-1], 1.0
    elif unit.endswith("b"):
        unit, scale = unit[:-1], 1 / 8
    else:
        scale = 1.0
    if unit in _BINARY:
        return value * _BINARY[unit] * scale
    if unit in _DECIMAL:
        return value * _DECIMAL[unit] * scale
    raise ValueError(f"unknown size unit in {text!r}")
