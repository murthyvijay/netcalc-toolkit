import unittest

from netcalc.ccna import subnet


class TestSubnetInfo(unittest.TestCase):
    def test_slash26(self):
        info = subnet.subnet_info("192.168.10.77/26")
        self.assertEqual(info["network"], "192.168.10.64")
        self.assertEqual(info["broadcast"], "192.168.10.127")
        self.assertEqual(info["first_host"], "192.168.10.65")
        self.assertEqual(info["last_host"], "192.168.10.126")
        self.assertEqual(info["usable_hosts"], 62)
        self.assertEqual(info["wildcard"], "0.0.0.63")
        self.assertEqual(info["class"], "C")
        self.assertEqual(info["scope"], "private")

    def test_point_to_point(self):
        info = subnet.subnet_info("10.0.0.0/31")
        self.assertEqual(info["usable_hosts"], 2)
        self.assertEqual(info["first_host"], "10.0.0.0")

    def test_ipv6(self):
        info = subnet.subnet_info("2001:db8::1/64")
        self.assertEqual(info["network"], "2001:db8::")
        self.assertEqual(info["usable_hosts"], 2 ** 64)


class TestClasses(unittest.TestCase):
    def test_address_class(self):
        self.assertEqual(subnet.address_class("10.1.1.1"), "A")
        self.assertEqual(subnet.address_class("172.16.0.1"), "B")
        self.assertEqual(subnet.address_class("224.0.0.5"), "D")


class TestSizing(unittest.TestCase):
    def test_prefix_for_hosts(self):
        self.assertEqual(subnet.prefix_for_hosts(500), 23)
        self.assertEqual(subnet.prefix_for_hosts(62), 26)
        self.assertEqual(subnet.prefix_for_hosts(63), 25)
        self.assertEqual(subnet.prefix_for_hosts(2), 30)

    def test_split(self):
        self.assertEqual(subnet.split("10.0.0.0/22", 24),
                         ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"])


if __name__ == "__main__":
    unittest.main()
