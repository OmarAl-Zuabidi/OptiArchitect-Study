"""
Reproducible validation of OptiArchitect against independent reference solvers (SciPy).

    pip install scipy
    python validation/run_validation.py            # writes validation/results.json

LP ................ simplex methods   vs  scipy.optimize.linprog (HiGHS)
Transportation .... NWC/LC/VAM + MODI vs  linprog on the transportation LP
Assignment ........ Hungarian         vs  scipy.optimize.linear_sum_assignment
Non-linear 1-D .... all methods       vs  analytically known minimisers
"""
import json
import math
import os
import time

import numpy as np
from scipy.optimize import linear_sum_assignment, linprog

from optiarchitect import (Objective, hungarian, solve_lp, solve_transportation)
from optiarchitect.core import run_method, diagnose

SEED = 20260607
rng = np.random.default_rng(SEED)
OUT = {"seed": SEED}


def rel(a, b):
    return abs(a - b) / (1.0 + abs(b))


# ---------------------------------------------------------------- LP
def lp_reference(c, A, b, types, obj):
    sgn = -1.0 if obj == "max" else 1.0
    Aub, bub, Aeq, beq = [], [], [], []
    for row, bi, t in zip(A, b, types):
        if t == "<=":
            Aub.append(row); bub.append(bi)
        elif t == ">=":
            Aub.append(-row); bub.append(-bi)
        else:
            Aeq.append(row); beq.append(bi)
    r = linprog(sgn * c, A_ub=np.array(Aub) if Aub else None, b_ub=bub or None,
                A_eq=np.array(Aeq) if Aeq else None, b_eq=beq or None, bounds=(0, None), method="highs")
    status = {0: "optimal", 2: "infeasible", 3: "unbounded"}.get(r.status, "other")
    if status == "infeasible":
        # SciPy reports HiGHS' ambiguous "infeasible or unbounded" presolve outcome as status 2.
        # Disambiguate with an independent feasibility LP (zero objective).
        f = linprog(np.zeros_like(c), A_ub=np.array(Aub) if Aub else None, b_ub=bub or None,
                    A_eq=np.array(Aeq) if Aeq else None, b_eq=beq or None, bounds=(0, None), method="highs")
        if f.status == 0:
            status = "unbounded"
    return status, (sgn * r.fun if r.status == 0 else None)


def lp_study(N=1000):
    stats = dict(n=N, agree_status=0, optimal=0, infeasible=0, unbounded=0, max_rel_err=0.0,
                 by_method={"standard": 0, "dual": 0, "two_phase": 0}, mism=[])
    for k in range(N):
        n, m = int(rng.integers(2, 8)), int(rng.integers(2, 8))
        A = rng.integers(-4, 10, size=(m, n)).astype(float)
        b = rng.integers(-5, 40, size=m).astype(float)
        c = rng.integers(-6, 12, size=n).astype(float)
        types = list(rng.choice(["<=", ">=", "="], size=m, p=[0.55, 0.3, 0.15]))
        obj = str(rng.choice(["max", "min"]))
        ref_s, ref_z = lp_reference(c, A, b, types, obj)
        res = solve_lp(c, A, b, types, obj)
        stats["by_method"][res.method] += 1
        if ref_s == res.status:
            stats["agree_status"] += 1
            stats[res.status] += 1
            if res.status == "optimal":
                stats["max_rel_err"] = max(stats["max_rel_err"], rel(res.z, ref_z))
                assert res.max_violation < 1e-7
        else:
            stats["mism"].append([k, ref_s, res.status])
    return stats


# ---------------------------------------------------------------- Transportation
def tp_reference(C, S, D):
    m, n = C.shape
    ts, td = S.sum(), D.sum()
    Aub, bub, Aeq, beq = [], [], [], []
    for i in range(m):
        row = np.zeros(m * n); row[i * n:(i + 1) * n] = 1
        (Aeq if ts <= td + 1e-12 else Aub).append(row)
        (beq if ts <= td + 1e-12 else bub).append(S[i])
    for j in range(n):
        row = np.zeros(m * n); row[j::n] = 1
        (Aub if ts <= td + 1e-12 else Aeq).append(row)
        (bub if ts <= td + 1e-12 else beq).append(D[j])
    if abs(ts - td) <= 1e-12:
        Aub, bub = [], []
        Aeq, beq = [], []
        for i in range(m):
            row = np.zeros(m * n); row[i * n:(i + 1) * n] = 1; Aeq.append(row); beq.append(S[i])
        for j in range(n):
            row = np.zeros(m * n); row[j::n] = 1; Aeq.append(row); beq.append(D[j])
    r = linprog(C.ravel(), A_ub=np.array(Aub) if Aub else None, b_ub=bub or None,
                A_eq=np.array(Aeq) if Aeq else None, b_eq=beq or None, bounds=(0, None), method="highs")
    return r.fun


def tp_study(N=500):
    st = dict(n=N, unbalanced=0, degenerate_repaired=0, max_rel_err=0.0, ok_all_starts=0,
              improvement={"nw": [], "lc": [], "vam": []}, iters={"nw": [], "lc": [], "vam": []})
    for k in range(N):
        m, n = int(rng.integers(2, 9)), int(rng.integers(2, 9))
        C = rng.integers(1, 51, size=(m, n)).astype(float)
        small = rng.random() < 0.4                     # small integers -> many ties / degeneracy
        S = rng.integers(1, 6 if small else 60, size=m).astype(float) * (5 if small else 1)
        D = rng.integers(1, 6 if small else 60, size=n).astype(float) * (5 if small else 1)
        if rng.random() < 0.5:                          # force a balanced instance
            D = D * (S.sum() / D.sum())
            D = np.round(D)
            D[-1] += S.sum() - D.sum()
            if D.min() < 0:
                continue
        ref = tp_reference(C, S, D)
        okc = True
        for start in ("nw", "lc", "vam"):
            r = solve_transportation(C, S, D, start=start)
            err = rel(r.solution.cost, ref)
            st["max_rel_err"] = max(st["max_rel_err"], err)
            okc &= (r.solution.status == "optimal" and err < 1e-7 and r.max_residual < 1e-7)
            st["iters"][start].append(len(r.solution.iterations))
            st["improvement"][start].append(r.ibfs[start].cost / ref)
            if start == "vam":
                st["degenerate_repaired"] += int(r.solution.zero_cells_added > 0)
                st["unbalanced"] += int(r.dummy is not None)
        st["ok_all_starts"] += int(okc)
    for key in ("improvement", "iters"):
        st[key] = {s: float(np.mean(v)) for s, v in st[key].items()}
    return st


# ---------------------------------------------------------------- Assignment
def as_study(N=1000):
    st = dict(n=N, exact=0, rectangular=0, maximize=0, max_abs_err=0.0)
    for _ in range(N):
        r, c = int(rng.integers(1, 10)), int(rng.integers(1, 10))
        C = rng.integers(1, 100, size=(r, c)).astype(float)
        mx = bool(rng.random() < 0.5)
        res = hungarian(C, maximize=mx)
        ri, ci = linear_sum_assignment(C, maximize=mx)
        ref = C[ri, ci].sum()
        err = abs(res.cost - ref)
        st["max_abs_err"] = max(st["max_abs_err"], err)
        st["exact"] += int(err < 1e-9)
        st["rectangular"] += int(r != c)
        st["maximize"] += int(mx)
    return st


# ---------------------------------------------------------------- NLP
NLP_CASES = [
    ("(x-2)**2+1", 1, 0.0, 5.0, 2.0, 2.5, 3.0),
    ("x*exp(-x)", -1, 0.0, 5.0, 1.0, 0.5, 0.8),
    ("x**4-3*x**3+2", 1, 0.0, 3.0, 2.25, 1.5, 2.0),
    ("exp(x)-2*x", 1, -2.0, 3.0, math.log(2), 0.0, 0.5),
    ("x+1/x", 1, 0.1, 5.0, 1.0, 1.5, 2.0),
    ("cos(x)", 1, 2.0, 5.0, math.pi, 3.5, 4.0),
    ("x**2*log(x)", 1, 0.1, 2.0, math.exp(-0.5), 0.8, 1.0),
    ("sin(x)+x/2", -1, 0.0, 3.0, 2 * math.pi / 3, 1.0, 1.5),
]


def nlp_study():
    rows = []
    for text, sign, a, b, xt, x0, x1 in NLP_CASES:
        o = Objective(text, sign)
        diag = diagnose(o, a, b, x0, x1)
        row = dict(f=text, goal="max" if sign == -1 else "min", a=a, b=b, xstar=xt, errs={}, evals={})
        for meth in ("golden", "fibonacci", "newton", "secant"):
            if not diag[meth][0]:
                row["errs"][meth] = None
                continue
            r = run_method(o, meth, a, b, x0, x1, 1e-8)
            row["errs"][meth] = abs(r.x - xt) if r.status == "converged" else None
            row["evals"][meth] = r.evals
        rows.append(row)
    return rows


# ---------------------------------------------------------------- Scaling
def scaling():
    out = []
    for n in (10, 25, 50, 100, 200):
        m = n
        A = rng.integers(1, 10, size=(m, n)).astype(float)
        b = rng.integers(50, 200, size=m).astype(float)
        c = rng.integers(1, 20, size=n).astype(float)
        t0 = time.perf_counter(); res = solve_lp(c, A, b, ["<="] * m, "max"); t1 = time.perf_counter()
        _, zref = lp_reference(c, A, b, ["<="] * m, "max"); t2 = time.perf_counter()
        out.append(dict(n=n, m=m, ours_s=t1 - t0, highs_s=t2 - t1, iters=res.iterations,
                        rel_err=rel(res.z, zref)))
    return out


if __name__ == "__main__":
    t = time.time()
    OUT["lp"] = lp_study(); print("LP done", OUT["lp"]["agree_status"], "/", OUT["lp"]["n"])
    OUT["transport"] = tp_study(); print("TP done", OUT["transport"]["ok_all_starts"], "/", OUT["transport"]["n"])
    OUT["assignment"] = as_study(); print("AS done", OUT["assignment"]["exact"], "/", OUT["assignment"]["n"])
    OUT["nlp"] = nlp_study()
    OUT["scaling"] = scaling()
    OUT["elapsed_s"] = time.time() - t
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
    with open(path, "w") as fh:
        json.dump(OUT, fh, indent=2, default=float)
    print("saved", path)
