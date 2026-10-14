"""Linear programming: automatic method routing, independent verification, step-by-step trace.

Run:  python examples/01_linear_programming.py
"""
from optiarchitect import solve_lp
from optiarchitect.core.lp import lp_applicability

MODELS = {
    "max 3x1+5x2, all rows <=  (standard simplex)": dict(
        c=[3, 5], A=[[1, 0], [0, 2], [3, 2]], b=[4, 12, 18], types=["<="] * 3, obj="max"),
    "min 2x1+3x2, rows >=      (dual simplex)": dict(
        c=[2, 3], A=[[1, 1], [1, 3]], b=[4, 6], types=[">="] * 2, obj="min"),
    "max 3x1+2x2, one equality (two-phase)": dict(
        c=[3, 2], A=[[1, 1], [1, 0]], b=[4, 3], types=["=", "<="], obj="max"),
    "x1 <= 1 and x1 >= 2": dict(
        c=[1], A=[[1], [1]], b=[1, 2], types=["<=", ">="], obj="max"),
    "max x1 s.t. x1 - x2 <= 1": dict(
        c=[1, 0], A=[[1, -1]], b=[1], types=["<="], obj="max"),
}

for title, m in MODELS.items():
    res = solve_lp(m["c"], m["A"], m["b"], m["types"], m["obj"])          # method="auto"
    print(f"{title}\n    method={res.method:9s} status={res.status:10s} z={res.z}  x={res.x}"
          f"  pivots={res.iterations}  max_violation={res.max_violation}")

# Which methods could start on the first model, and why?
m = list(MODELS.values())[0]
print("\napplicability report for the first model:")
for method, (ok, reason_key) in lp_applicability(m["c"], m["b"], m["types"], m["obj"]).items():
    print(f"    {method:9s} applicable={ok}  ({reason_key})")

# Step-by-step: a trace callback receives every tableau; the solver itself never prints.
tableaux = []
solve_lp(m["c"], m["A"], m["b"], m["types"], m["obj"],
         trace=lambda T, basis, names, title: tableaux.append(title))
print("\ntableaux recorded by the trace callback:", tableaux)
