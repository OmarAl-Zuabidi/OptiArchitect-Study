"""The scripts in examples/ must keep working and keep printing the documented results."""
import contextlib
import io
import os
import runpy
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_example(name):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        runpy.run_path(os.path.join(ROOT, "examples", name), run_name="__main__")
    return out.getvalue()


class ExampleScripts(unittest.TestCase):
    def test_linear_programming(self):
        out = run_example("01_linear_programming.py")
        self.assertIn("method=standard  status=optimal    z=36.0", out)
        self.assertIn("method=dual      status=optimal    z=9.0", out)
        self.assertIn("method=two_phase status=infeasible", out)
        self.assertIn("status=unbounded", out)

    def test_transportation_assignment(self):
        out = run_example("02_transportation_assignment.py")
        self.assertIn("optimal cost           : 225.0", out)
        self.assertIn("total profit              : 42.0", out)

    def test_nonlinear(self):
        out = run_example("03_nonlinear_1d.py")
        self.assertIn("newton    applicable=False reason=newton_curv", out)
        self.assertIn("unsafe formula rejected", out)
        self.assertEqual(out.count("converged  x*=1.0000000"), 4)


if __name__ == "__main__":
    unittest.main()
