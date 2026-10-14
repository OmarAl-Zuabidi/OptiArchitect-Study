# Methods, routing and verification

## Linear programming

| Situation (maximisation form) | Method used |
|---|---|
| all rows `<=` and `b >= 0` | standard (primal) simplex from the slack basis |
| no `=` rows and `c <= 0` | dual simplex (rows `>=` are negated; a negative right-hand side is handled directly) |
| otherwise | two-phase simplex (artificial variables, removal of redundant rows) |

Pivoting uses Dantzig's rule and switches to Bland's rule after 25 consecutive degenerate pivots.
Statuses: `optimal`, `infeasible`, `unbounded`, `iteration_limit` (cap 10,000 pivots, always reported).
Verification: for an optimal answer, `max_violation` is the largest violation of any constraint or of `x >= 0`,
computed from the original data, not from the tableau. A user may force a method only if it can start on the model.

## Transportation

Unbalanced problems get a zero-cost dummy source or destination. Starting solutions: North-West Corner, Least
Cost (ties to the larger shipment) and Vogel's approximation (a line with one remaining cell has infinite penalty).
`start="best"` picks the cheapest (ties prefer Vogel) and improves it with MODI: dual potentials `u, v` are computed on
the basis tree, the most negative net evaluation enters, and the stepping-stone loop is the unique tree path. A
degenerate basis is completed to a spanning tree of `m + n - 1` cells using the cheapest zero cells (reported as
`zero_cells_added`). Non-basic cells with zero net evaluation set `alternative_optima`.
Verification: `max_residual` compares row and column sums with supplies and demands.

## Assignment

Hungarian method: row and column reduction, then a maximum zero matching and a minimum line cover (Konig's
construction) with matrix adjustments until the matching is perfect. Rectangular matrices are padded with a
dummy row or column, maximisation uses `max(C) - C`, and unmatched rows or columns are reported.

## Single-variable non-linear optimization

The user's `f` is minimised as `g = sign * f` (`sign = -1` for maximisation).
Golden Section and Fibonacci search use only values; Newton-Raphson and secant use first and second derivatives
(symbolic through SymPy, central finite differences when no symbolic derivative exists). `diagnose` decides
which methods are applicable and why: a dense scan tests unimodality (a multimodal sample is a caution, not a veto);
Newton needs `f''(x0) > 0`; secant needs two distinct starting points with a defined `f'`. Statuses:
`converged`, `max_iter`, `zero_curvature`, `not_minimum`, `left_interval`, `diverged`, `domain_error`.
Verification: the best converged result is compared with a dense grid scan.

## Safe formulas

User formulas are checked against an abstract-syntax-tree white-list before they reach SymPy: the variable `x`,
the constants `pi` and `E`, 14 elementary functions with one argument, numbers up to 1e6 in magnitude, at most 200
characters, no attribute access, no nested constant powers. Nothing is passed to `eval`.

## Independent validation

`validation/run_validation.py` (fixed seed) compares the solvers with SciPy on random instances; the figures
obtained for release 1.0.0 are stored in `validation/results.json`:

| Study | Instances | Reference | Result |
|---|---|---|---|
| LP (mixed relations) | 1,000 | HiGHS via `scipy.optimize.linprog` | status agrees in 1,000; objective differs by at most 1.8e-14 (relative) |
| Transportation x 3 starting rules | 500 | LP optimum | every start reaches the optimum (1,500 runs) |
| Assignment | 1,000 | `scipy.optimize.linear_sum_assignment` | exact agreement |
| 1-D non-linear | 8 functions | known minimisers | all applicable runs converge; largest error 2.7e-8 |
