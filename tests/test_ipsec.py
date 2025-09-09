import unittest

from netcalc.protocols import ipsec


class TestPadding(unittest.TestCase):
    def test_block_alignment(self):
        self.assertEqual(ipsec.padding(14, 16), 0)
        self.assertEqual(ipsec.padding(1400, 16), 6)
        self.assertEqual(ipsec.padding(1400, 4), 2)


class TestPacketSize(unittest.TestCase):
    def test_tunnel_gcm(self):
        self.assertEqual(ipsec.esp_packet_size(1400, "aes-gcm"), 1456)
        self.assertEqual(ipsec.esp_overhead(1400, "aes-gcm"), 56)

    def test_nat_t_and_cbc(self):
        self.assertEqual(ipsec.esp_packet_size(1400, "aes-cbc-sha1", nat_t=True), 1472)

    def test_transport_mode_is_smaller(self):
        self.assertEqual(ipsec.esp_packet_size(1400, "aes-gcm", tunnel=False), 1436)

    def test_ipv6_outer(self):
        self.assertEqual(ipsec.esp_packet_size(1400, "aes-gcm", outer_ip=6), 1476)
