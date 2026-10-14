"""Tests of the interactive console program (scripted input, no terminal needed)."""
import contextlib
import io
import unittest
from unittest import mock

from optiarchitect.cli import main


def run_cli(argv, answers=()):
    out = io.StringIO()
    it = iter(answers)
    with mock.patch("builtins.input", lambda prompt="": next(it)), contextlib.redirect_stdout(out):
        code = main(argv)
    return code, out.getvalue()


class ConsoleTests(unittest.TestCase):
    def test_selftest_passes(self):
        code, out = run_cli(["--selftest", "--lang", "en"])
        self.assertEqual(code, 0)
        self.assertIn("15/15", out)

    def test_selftest_arabic(self):
        code, _ = run_cli(["--selftest", "--lang", "ar"])
        self.assertEqual(code, 0)

    def test_menu_and_worked_examples(self):
        # name -> Part n -> [2] worked example -> pick -> back -> exit
        for part, ex in ((1, 1), (1, 3), (2, 1), (2, 4), (3, 2)):
            with self.subTest(part=part, ex=ex):
                code, out = run_cli(["--lang", "en", "--no-plot"], ["", str(part), "2", str(ex), "0", "0"])
                self.assertEqual(code, 0)
                self.assertIn("solution verified", out)

    def test_own_problem_lp(self):
        # Example 1 typed by hand: max 3x1+5x2 s.t. x1<=4, 2x2<=12, 3x1+2x2<=18
        answers = ["", "1", "1", "1", "2", "3", "3", "5",
                   "1", "0", "1", "4", "0", "2", "1", "12", "3", "2", "1", "18",
                   "1", "", "0", "0"]
        code, out = run_cli(["--lang", "en", "--no-plot"], answers)
        self.assertEqual(code, 0)
        self.assertIn("Optimal objective value (Z) = 36.000000", out)

    def test_invalid_input_is_reprompted(self):
        code, out = run_cli(["--lang", "en"], ["", "x", "0"])      # 'x' is not a menu number
        self.assertEqual(code, 0)
        self.assertIn("Invalid numeric value", out)

    def test_about_shows_repository(self):
        for lang in ("en", "ar"):
            code, out = run_cli(["--lang", lang], ["", "8", "", "0"])      # menu [8] About, Enter, exit
            self.assertEqual(code, 0)
            self.assertIn("github.com/OmarAl-Zuabidi/OptiArchitect-Suite", out)
            self.assertNotIn("to be completed", out)

    def test_version(self):
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            main(["--version"])
        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
