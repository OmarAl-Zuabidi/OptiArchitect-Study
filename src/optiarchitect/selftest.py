"""
OptiArchitect built-in verification suite (pure function, no printing).

Reproduces the reference results, cross-validates the solvers against each other
(MODI vs simplex, Hungarian vs brute force) and checks the EN/AR message tables.
Returns a list of (label, result) with result True / False / None (skipped).
"""
import itertools
import math
import os
import string
import tempfile

import numpy as np

from optiarchitect.core import (solve_lp, solve_transportation, hungarian, golden_section,
                  fibonacci_search, newton_raphson, secant_method)
from optiarchitect.examples import LP_EXAMPLES, TP_EXAMPLES, AS_EXAMPLES
from optiarchitect.messages import TEXT
from optiarchitect.utils.parser import Objective, sp


def run_selftest():
    close = lambda a, b, t=1e-6: abs(a - b) <= t * (1.0 + abs(b))   # noqa: E731

    def lp(c, A, b, t, o):
        return solve_lp(c, A, b, t, o)

    def transport_via_lp(C, S, D):
        r = solve_transportation(C, S, D)
        Cb, Sb, Db = r.C, r.S, r.D
        m, n = Cb.shape
        rows, rhs, types = [], [], []
        for i in range(m):
            row = np.zeros(m * n); row[i * n:(i + 1) * n] = 1; rows.append(row); rhs.append(Sb[i]); types.append("=")
        for j in range(n):
            row = np.zeros(m * n); row[j::n] = 1; rows.append(row); rhs.append(Db[j]); types.append("=")
        ref = solve_lp(Cb.ravel(), np.array(rows), rhs, types, "min")
        return r, ref

    def assign_bruteforce(C, maximize):
        C = np.asarray(C, float)
        r, c = C.shape
        vals = []
        if r <= c:
            for p in itertools.permutations(range(c), r):
                vals.append(sum(C[i, j] for i, j in enumerate(p)))
        else:
            for p in itertools.permutations(range(r), c):
                vals.append(sum(C[i, j] for j, i in enumerate(p)))
        return max(vals) if maximize else min(vals)

    def placeholders(text):
        return {f for _, f, _, _ in string.Formatter().parse(text) if f}

    checks = []

    def add(label, fn):
        checks.append((label, fn))

    add("LP 1  Standard Simplex : Z = 36, x = (2, 6)", lambda: (
        lambda r: r.status == "optimal" and r.method == "standard" and close(r.z, 36)
        and np.allclose(r.x, [2, 6]))(lp([3, 5], [[1, 0], [0, 2], [3, 2]], [4, 12, 18], ["<=", "<=", "<="], "max")))
    add("LP 2  Dual Simplex     : Z = 9,  x = (3, 1)", lambda: (
        lambda r: r.status == "optimal" and r.method == "dual" and close(r.z, 9)
        and np.allclose(r.x, [3, 1]))(lp([2, 3], [[1, 1], [1, 3]], [4, 6], [">=", ">="], "min")))
    add("LP 3  Two-Phase        : Z = 11, x = (3, 1)", lambda: (
        lambda r: r.status == "optimal" and r.method == "two_phase" and close(r.z, 11)
        and np.allclose(r.x, [3, 1]))(lp([3, 2], [[1, 1], [1, 0]], [4, 3], ["=", "<="], "max")))
    add("LP 4  infeasible model detected",
        lambda: lp([1], [[1], [1]], [1, 2], ["<=", ">="], "max").status == "infeasible")
    add("LP 5  unbounded model detected",
        lambda: lp([1, 0], [[1, -1]], [1], ["<="], "max").status == "unbounded")

    def tp_check(k):
        d = TP_EXAMPLES[k]
        r, ref = transport_via_lp(d["C"], d["S"], d["D"])
        return (r.solution.status == "optimal" and ref.status == "optimal"
                and close(r.solution.cost, ref.z) and r.max_residual < 1e-7)
    add("TP 1  MODI cost == simplex optimum (balanced)", lambda: tp_check(1))
    add("TP 2  MODI cost == simplex optimum (dummy destination)", lambda: tp_check(2))

    def as_check(k):
        d = AS_EXAMPLES[k]
        return close(hungarian(d["C"], d["maximize"]).cost, assign_bruteforce(d["C"], d["maximize"]))
    add("AS 1  Hungarian == brute force (4x4, min)", lambda: as_check(3))
    add("AS 2  Hungarian == brute force (3x4, max, padded)", lambda: as_check(4))

    def plot_check():
        try:
            import matplotlib
            matplotlib.use("Agg")
        except ImportError:
            return None
        from optiarchitect.utils.plot import plot_feasible_region
        d = LP_EXAMPLES[1]
        res = solve_lp(d["c"], d["A"], d["b"], d["types"], d["obj"])
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "lp.png")
            plot_feasible_region(d["c"], d["A"], d["b"], d["types"], d["obj"], res, show=False, save_path=path)
            return os.path.getsize(path) > 1000
    add("LP 6  graphical method renders the feasible region", plot_check)

    def nl_check():
        if sp is None:
            return None
        o = Objective("(x-2)**2+1")
        rs = [golden_section(o.f, 0, 5, 1e-8), fibonacci_search(o.f, 0, 5, 1e-8),
              newton_raphson(o.f, o.df, o.d2f, 2.5), secant_method(o.f, o.df, 2.5, 3.0, d2f=o.d2f)]
        return all(r.status == "converged" and abs(r.x - 2) < 1e-6 for r in rs)
    add("NL 1  Golden / Fibonacci / Newton / Secant find x* = 2", nl_check)

    def nl_max():
        if sp is None:
            return None
        o = Objective("x*exp(-x)", -1)
        r = golden_section(o.f, 0, 5, 1e-8)
        return abs(r.x - 1) < 1e-5 and close(o.user_value(r.fx), math.exp(-1), 1e-8)
    add("NL 2  maximization through sign change: x* = 1", nl_max)

    def nl_safe():
        if sp is None:
            return None
        for bad in ("__import__('os').system('echo x')", "x.__class__", "open('f')", "2x"):
            try:
                Objective(bad)
                return False
            except ValueError:
                pass
        return True
    add("NL 3  unsafe formulas are rejected", nl_safe)

    add("I18N  English/Arabic tables have identical keys", lambda: set(TEXT["en"]) == set(TEXT["ar"]))
    add("I18N  placeholders agree between languages", lambda: all(
        placeholders(TEXT["en"][k]) == placeholders(TEXT["ar"][k]) for k in TEXT["en"]))

    out = []
    for label, fn in checks:
        try:
            r = fn()
        except Exception as e:                       # a crashing check is a failed check
            r = False
            label += f"  ({type(e).__name__}: {e})"
        out.append((label, r))
    return out
