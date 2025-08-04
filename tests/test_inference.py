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


class TestDecode(unittest.TestCase):
    def test_memory_bound_rate(self):
        per_seq, total = inference.decode_tokens_per_second(140e9, 3.35e12)
        self.assertAlmostEqual(per_seq, 23.93, places=2)
        self.assertEqual(per_seq, total)

    def test_batching_trades_latency_for_throughput(self):
        one, _ = inference.decode_tokens_per_second(140e9, 3.35e12, 1, 1e9)
        per_seq, total = inference.decode_tokens_per_second(140e9, 3.35e12, 16, 1e9)
        self.assertLess(per_seq, one)
        self.assertGreater(total, one)

    def test_max_batch(self):
        self.assertEqual(inference.max_batch_for_memory(192e9, 140e9, 1.3e9), 40)
        self.assertEqual(inference.max_batch_for_memory(80e9, 140e9, 1e9), 0)


if __name__ == "__main__":
    unittest.main()
