import contextlib
import io
import unittest

from netcalc.__main__ import TOOLS, main


class TestDispatcher(unittest.TestCase):
    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(list(argv))
        return code, out.getvalue()

    def test_lists_every_tool(self):
        code, out = self.run_cli()
        self.assertEqual(code, 0)
        for name in TOOLS:
            self.assertIn(name, out)

    def test_runs_a_tool(self):
        code, out = self.run_cli("subnet", "info", "10.0.0.1/30")
        self.assertEqual(code, 0)
        self.assertIn("10.0.0.3", out)

    def test_unknown_tool(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["nope"]), 2)


if __name__ == "__main__":
    unittest.main()
