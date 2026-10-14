"""
Smoke tests for the web front end (app.py) using a fake Streamlit module.
They check that every page / part / worked example renders in both languages without
errors, that user-input flows give the reference numbers, and that validation messages
are the same ones the console program shows.   Run:  python -m unittest tests.test_app_smoke
"""
import html
import re
import unittest

import pandas as pd

from tests import fake_streamlit as fs


def text(fake):
    return html.unescape(re.sub(r"<(?!PYPLOT)[^>]+>", "", "\n".join(fake.out)))


class AppSmoke(unittest.TestCase):
    def run_app(self, state, pressed=(), editors=None):
        return fs.run({"state": state, "pressed": set(pressed), "editors": editors or {}})

    def test_every_page_both_languages(self):
        for lang in ("en", "ar"):
            for page in ("home", "guide", "about", "selftest", "part1", "part2", "part3"):
                with self.subTest(lang=lang, page=page):
                    f = self.run_app({"lang": lang, "page": page, "mode_1": "learn", "mode_2": "learn",
                                      "mode_3": "learn"}, {"run_selftest"} if page == "selftest" else ())
                    self.assertIn("OPTIARCHITECT", text(f))

    def test_selftest_all_pass(self):
        f = self.run_app({"page": "selftest"}, {"run_selftest"})
        self.assertIn("15/15", text(f))

    def test_worked_examples_verified(self):
        for lang in ("en", "ar"):
            for part, n in ((1, 3), (2, 4), (3, 3)):
                for ex in range(1, n + 1):
                    for detail in (False, True):
                        with self.subTest(lang=lang, part=part, ex=ex, detail=detail):
                            f = self.run_app({"lang": lang, "page": f"part{part}", f"mode_{part}": "ex",
                                              f"ex_pick_{part}": ex, "detail": detail}, {f"run_ex_{part}"})
                            t = text(f)
                            self.assertNotIn("[X] Error", t)
                            self.assertIn(fs.TEXT_OK[lang], t)

    def test_lp_own_problem(self):
        xs = ["x1", "x2"]
        c = pd.DataFrame([[3.0, 5.0]], columns=xs, index=["Z"])
        k = pd.DataFrame([[1, 0, "<=", 4.0], [0, 2, "<=", 12.0], [3, 2, "<=", 18.0]],
                         columns=xs + ["rel", "rhs"], index=["C1", "C2", "C3"])
        f = self.run_app({"page": "part1", "mode_1": "own", "lp_n": 2, "lp_m": 3}, {"lp_go"},
                         {"lp_c_2": c, "lp_k_2_3": k})
        t = text(f)
        self.assertIn("Optimal objective value (Z) = 36.000000", t)
        self.assertIn("<PYPLOT>", t)

    def test_validation_messages(self):
        cases = [({"page": "part2", "mode_2": "own"}, "tp_go", "Total must be greater than 0"),
                 ({"page": "part3", "mode_3": "own", "nl_a": 6.0, "nl_b": 5.0}, "nl_go", "b must be greater than a"),
                 ({"page": "part3", "mode_3": "own", "nl_tol": "abc"}, "nl_go", "Invalid numeric value"),
                 ({"page": "part3", "mode_3": "own", "nl_text": "__import__('os')"}, "nl_go", "Invalid expression")]
        for state, btn, msg in cases:
            with self.subTest(msg=msg):
                self.assertIn(msg, text(self.run_app(state, {btn})))


if __name__ == "__main__":
    unittest.main()
