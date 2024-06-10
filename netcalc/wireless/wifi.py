"""Wi-Fi channels and 802.11n/ac/ax PHY data rates.

The PHY rate of an OFDM Wi-Fi link is::

    rate = Nss * Nsd * bits_per_subcarrier * coding_rate / (T_symbol + GI)

where ``Nss`` is the number of spatial streams and ``Nsd`` the data
subcarriers for the channel width. 802.11ac (VHT) uses 3.2 us symbols with
a 0.8 us (or short 0.4 us) guard interval; 802.11ax (HE) uses 4x longer
12.8 us symbols with 0.8, 1.6 or 3.2 us guards and about 4x as many
subcarriers, plus 1024-QAM (MCS 10-11).

Channel centre frequencies: 2.4 GHz ``2407 + 5 ch`` MHz (channel 14 is
2484), 5 GHz ``5000 + 5 ch`` MHz, 6 GHz ``5950 + 5 ch`` MHz.

Usage::

    python -m netcalc.wireless.wifi rate --std ax --mcs 11 --width 80 --nss 2
    python -m netcalc.wireless.wifi table --std ac --width 80
    python -m netcalc.wireless.wifi channel --band 6 --ch 37
    python -m netcalc.wireless.wifi airtime --bytes 1500 --rate 600
"""

import argparse

# MCS index -> (bits per subcarrier, coding rate)
MCS = {
    0: (1, 1 / 2), 1: (2, 1 / 2), 2: (2, 3 / 4), 3: (4, 1 / 2), 4: (4, 3 / 4), 5: (6, 2 / 3),
    6: (6, 3 / 4), 7: (6, 5 / 6), 8: (8, 3 / 4), 9: (8, 5 / 6), 10: (10, 3 / 4), 11: (10, 5 / 6),
}
DATA_SUBCARRIERS = {
    "n": {20: 52, 40: 108},
    "ac": {20: 52, 40: 108, 80: 234, 160: 468},
    "ax": {20: 234, 40: 468, 80: 980, 160: 1960},
}
MODULATION = {1: "BPSK", 2: "QPSK", 4: "16-QAM", 6: "64-QAM", 8: "256-QAM", 10: "1024-QAM"}
SYMBOL_US = {"n": 3.2, "ac": 3.2, "ax": 12.8}
MAX_MCS = {"n": 7, "ac": 9, "ax": 11}
BAND_BASE_MHZ = {"2.4": 2407, "5": 5000, "6": 5950}


def phy_rate_mbps(std, mcs, width_mhz, nss=1, gi_us=0.8):
    """PHY data rate in Mb/s for a standard (``n``, ``ac``, ``ax``).

    >>> round(phy_rate_mbps("ax", 11, 80), 1)
    600.5
    >>> round(phy_rate_mbps("ac", 9, 80))
    390
    """
    std = std.lower()
    if mcs > MAX_MCS[std]:
        raise ValueError(f"802.11{std} has no MCS {mcs}")
    bits, rate = MCS[mcs]
    nsd = DATA_SUBCARRIERS[std][width_mhz]
    return nss * nsd * bits * rate / (SYMBOL_US[std] + gi_us)


def rate_table(std, width_mhz, nss=1, gi_us=0.8):
    """``[(mcs, Mb/s), ...]`` for every MCS the standard defines."""
    return [(m, phy_rate_mbps(std, m, width_mhz, nss, gi_us)) for m in range(MAX_MCS[std.lower()] + 1)]


def channel_mhz(band, channel):
    """Centre frequency (MHz) of a Wi-Fi channel in the 2.4, 5 or 6 GHz band."""
    if band == "2.4" and channel == 14:
        return 2484
    return BAND_BASE_MHZ[band] + 5 * channel
