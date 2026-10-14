"""Single-variable optimization: safe formulas, method diagnosis, verified results.

Run:  python examples/03_nonlinear_1d.py
"""
from optiarchitect import Objective
from optiarchitect.core import diagnose, grid_minimum, run_method

# --- maximise f(x) = x*exp(-x) on [0, 5]: sign=-1 turns the problem into a minimisation of -f.
obj = Objective("x*exp(-x)", sign=-1)
print("f'(x)  =", obj.df_text, "   f''(x) =", obj.d2f_text, "   symbolic derivatives:", obj.symbolic)
a, b, x0, x1, tol = 0.0, 5.0, 0.5, 0.8, 1e-8
for method in ("golden", "fibonacci", "newton", "secant"):
    r = run_method(obj, method, a, b, x0, x1, tol)
    print(f"  {method:9s} {r.status:10s} x*={r.x:.7f}  f(x*)={obj.user_value(r.fx):.7f}  evals={r.evals}")
gx, gf = grid_minimum(obj.f, a, b)
print(f"  independent grid scan: x*={gx:.4f}  f(x*)={obj.user_value(gf):.7f}")

# --- the diagnosis step explains which methods are applicable.
obj = Objective("x**4-3*x**3+2")
print("\nf(x) = x^4 - 3x^3 + 2 on [0, 3], start 1.5")
for method, (ok, reason, params) in diagnose(obj, 0.0, 3.0, 1.5, 2.0).items():
    print(f"  {method:9s} applicable={ok!s:5s} reason={reason} {params}")

# --- formulas are validated against an AST white-list and never reach eval().
try:
    Objective("__import__('os').system('echo unsafe')")
except ValueError as exc:
    print("\nunsafe formula rejected:", exc)
