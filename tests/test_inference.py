import unittest

from netcalc.aifabric import inference


class TestKvCache(unittest.TestCase):
    def test_70b_class_model(self):
        self.assertEqual(inference.kv_bytes_per_token(80, 8, 128), 320 * 1024)

    def test_context_and_batch(self):
        total = inference.kv_cache_bytes(32768, 80, 8, 128)
        self.assertEqual(total, 10 * 1024 ** 3)
        self.assertEqual(inference.kv_cache_bytes(1024, 80, 8, 128, batch=4), 4 * 1024 * 327680)


class TestTransfer(unittest.TestCase):
    def test_prefill_to_decode(self):
        t = inference.kv_transfer_time(8192, 327680, 400e9, latency_s=10e-6)
        self.assertAlmostEqual(t, 10e-6 + 8192 * 327680 * 8 / 400e9)
