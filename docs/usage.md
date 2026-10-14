# Usage

OptiArchitect has three interfaces on one solver core: an interactive console, a web application and a Python API.
Everything the console and the web application print or ask exists in English and Arabic.

## 1. Interactive console

```bash
optiarchitect                      # or: python -m optiarchitect
optiarchitect --lang ar --part 2   # Arabic, open Part 2 directly
optiarchitect --detail             # show every tableau / MODI loop / iteration
optiarchitect --selftest           # run the built-in verification suite
```

Options: `--lang {en,ar}`, `--part {1,2,3}`, `--no-plot`, `--detail`, `--shape-ar`, `--selftest`, `--version`.
Type `?` at any prompt for help. Each part offers: solve your own problem, a pre-filled worked example with
"what to observe" notes, and a short description of its methods.

Excerpt of a real session (Part 1, worked example 1):

```text
 Applicability of each method to THIS model:
   [APPLICABLE] Standard Simplex: all rows are '<=' with RHS >= 0, so the slack basis is already feasible.
   [BYPASSED] Dual Simplex: needs an optimal-looking Z row at the start (maximize form: all c <= 0, e.g. MIN with c >= 0).
   [APPLICABLE] Two-Phase Simplex: always valid; artificial variables are removed in Phase I.
 * Recommended method: Standard Simplex

>>> Running: Standard Simplex

   ===== RESULTS (Analyst) =====
Status: OPTIMAL
   x1 = 2.000000
   x2 = 6.000000
Optimal objective value (Z) = 36.000000
Iterations: 2
Max constraint violation (independent check): 0.00e+00
```

## 2. Web application

```bash
pip install -e ".[web]"
optiarchitect-web                  # starts Streamlit; deep links: ?lang=ar&page=part2
```

Same menus, reports and message text as the console, with editable tables, step-by-step expanders,
CSV download of results and an interactive language switch.

## 3. Python API

```python
from optiarchitect import solve_lp, solve_transportation, hungarian, Objective
from optiarchitect.core import run_method

res = solve_lp([3, 5], [[1, 0], [0, 2], [3, 2]], [4, 12, 18], ["<="] * 3, "max")
print(res.method, res.status, res.z, res.x)        # standard optimal 36.0 [2. 6.]

tp = solve_transportation([[4, 6, 8, 5], [7, 3, 5, 6], [6, 8, 4, 7]], [20, 30, 25], [10, 25, 15, 10])
print(tp.dummy, tp.start, tp.solution.cost)        # destination vam 225.0

obj = Objective("x*exp(-x)", sign=-1)              # maximise; the formula is validated, never eval'ed
print(run_method(obj, "newton", 0, 5, 0.5, 0.8, 1e-8).x)   # 1.0 (to 8 digits)
```

Complete, runnable scripts with their output are in [`examples/`](../examples). Result objects are plain
dataclasses (see [api.md](api.md)); the solvers never print, raise no exception for mathematical outcomes such as
infeasibility (they return a status), and accept an optional `trace` callback for step-by-step display.
