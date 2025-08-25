"""IPsec ESP overhead and the largest inner packet that fits a path MTU.

An ESP packet wraps the protected payload as::

    [outer IP]  [UDP 4500 if NAT-T]  ESP header (SPI + seq, 8 B)  IV
    payload  padding  pad-length (1 B)  next-header (1 B)  ICV

The payload plus the 2 trailer bytes is padded to the cipher block size
(16 for AES-CBC, 4 for AES-GCM and ChaCha20, whose IV is 8 bytes). In tunnel
mode the payload is the whole inner IP packet and a new outer IP header is
added; in transport mode only the inner packet's payload is protected and
the original IP header is kept. ICVs: HMAC-SHA1-96 12 B, HMAC-SHA256-128
16 B, GCM 16 B.

Usage::

    python -m netcalc.protocols.ipsec size --inner 1400 --cipher aes-gcm
    python -m netcalc.protocols.ipsec size --inner 1400 --cipher aes-cbc-sha1 --nat-t
    python -m netcalc.protocols.ipsec mtu --path-mtu 1500 --cipher aes-gcm --nat-t
"""

import argparse

# name -> (iv bytes, block size, icv bytes)
CIPHERS = {
    "aes-gcm": (8, 4, 16),
    "chacha20-poly1305": (8, 4, 16),
    "aes-cbc-sha1": (16, 16, 12),
    "aes-cbc-sha256": (16, 16, 16),
}
ESP_HEADER = 8
ESP_TRAILER = 2
UDP_HEADER = 8
IP_HEADER = {4: 20, 6: 40}


def padding(payload_bytes, block):
    """Pad bytes so ``payload + padding + 2`` is a multiple of ``block``."""
    return (-(payload_bytes + ESP_TRAILER)) % block


def esp_packet_size(inner_bytes, cipher="aes-gcm", tunnel=True, nat_t=False, outer_ip=4,
                    inner_ip_header=20):
    """Size on the wire (IP packet bytes) of an ESP-protected packet.

    ``inner_bytes`` is the full inner IP packet; in transport mode its own
    IP header is kept outside ESP.

    >>> esp_packet_size(1400, "aes-gcm")
    1456
    """
    iv, block, icv = CIPHERS[cipher]
    payload = inner_bytes if tunnel else inner_bytes - inner_ip_header
    outer = IP_HEADER[outer_ip] if tunnel else inner_ip_header
    size = outer + ESP_HEADER + iv + payload + padding(payload, block) + ESP_TRAILER + icv
    return size + (UDP_HEADER if nat_t else 0)


def esp_overhead(inner_bytes, cipher="aes-gcm", tunnel=True, nat_t=False, outer_ip=4):
    """Bytes ESP adds to an inner packet of ``inner_bytes``."""
    return esp_packet_size(inner_bytes, cipher, tunnel, nat_t, outer_ip) - inner_bytes
