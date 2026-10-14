# API reference

Generated from the docstrings by `docs/generate_api.py`; do not edit by hand.
All solvers are pure functions: they never print and return the dataclasses listed here.

## Linear programming (`optiarchitect.core.lp`)

### `solve_lp`

```python
solve_lp(c, A, b, con_types, obj_type='max', method='auto', trace: Optional[Callable[[numpy.ndarray, List[int], List[str], str], NoneType]] = None) -> optiarchitect.core.lp.LPResult
```

Solve a linear program with ``x >= 0`` by the standard, dual or two-phase simplex method.

Never prints; returns an :class:`LPResult`.

Args:
    c: objective coefficients (length ``n``).
    A: constraint matrix of shape ``(m, n)``.
    b: right-hand sides (length ``m``).
    con_types: ``m`` relations, each ``"<="``, ``">="`` or ``"="``.
    obj_type: ``"max"`` or ``"min"``.
    method: ``"auto"`` (route with :func:`choose_method`), ``"standard"``, ``"dual"`` or
        ``"two_phase"``.
    trace: optional callback ``trace(T, basis, names, title)`` that receives the tableau at
        every iteration (this is how the console and web interfaces show the steps).

Returns:
    :class:`LPResult` with status ``"optimal"``, ``"infeasible"``, ``"unbounded"`` or
    ``"iteration_limit"``.

Raises:
    ValueError: for inconsistent dimensions, non-finite data, an invalid relation, or a forced
        ``method`` that cannot start on the model.

### `choose_method`

```python
choose_method(c_eff: numpy.ndarray, b: numpy.ndarray, types: Sequence[str]) -> str
```

Routing rule (c_eff is the objective in 'maximize' form).

standard  : all rows '<=' and b >= 0         -> slack basis is primal feasible
dual      : no '=' rows and c_eff <= 0       -> slack basis is DUAL feasible
            (rows '>=' are multiplied by -1; negative RHS is then handled directly)
two_phase : everything else (equalities, or no dual-feasible start)

### `lp_applicability`

```python
lp_applicability(c, b, types, obj) -> dict
```

Which LP method can start on this model, with the reason (message key).

### `max_violation`

```python
max_violation(A, b, types, x) -> float
```

Independent check: largest violation of any constraint or of x >= 0.

### `LPResult`

```python
class LPResult(status, method, x, z, iterations, max_violation, var_names)
```

Result of :func:`solve_lp`.

Attributes:
    status: ``"optimal"``, ``"infeasible"``, ``"unbounded"`` or ``"iteration_limit"``.
    method: ``"standard"``, ``"dual"`` or ``"two_phase"`` (the variant actually used).
    x: optimal point (``None`` unless optimal).
    z: objective value in the *original* sense (max or min), ``None`` unless optimal.
    iterations: simplex pivots performed.
    max_violation: largest violation of any constraint or of ``x >= 0``, computed
        independently of the tableau (``None`` unless optimal).
    var_names: names of the tableau columns.

## Transportation (`optiarchitect.core.transportation`)

### `solve_transportation`

```python
solve_transportation(C, S, D, start: str = 'best') -> optiarchitect.core.transportation.TransportResult
```

Solve a transportation problem: validate, balance, build the three starting solutions, optimise.

Never prints. An unbalanced problem receives a zero-cost dummy source or destination.

Args:
    C: unit-cost matrix of shape ``(m, n)``.
    S: supplies (length ``m``, non-negative, positive total).
    D: demands (length ``n``, non-negative, positive total).
    start: starting rule for MODI: ``"best"`` (cheapest of the three, ties prefer Vogel),
        ``"vam"``, ``"lc"`` or ``"nw"``.

Returns:
    :class:`TransportResult`; check ``result.solution.status`` and ``result.max_residual``.

Raises:
    ValueError: for inconsistent or non-finite data, negative supply or demand, or an unknown ``start``.

### `northwest_corner`

```python
northwest_corner(C, S, D) -> optiarchitect.core.transportation.IBFS
```

North-West Corner rule on balanced data; returns an :class:`IBFS`.
    

### `least_cost`

```python
least_cost(C, S, D) -> optiarchitect.core.transportation.IBFS
```

Least Cost rule on balanced data (ties go to the larger shipment); returns an :class:`IBFS`.
    

### `vogel`

```python
vogel(C, S, D) -> optiarchitect.core.transportation.IBFS
```

VAM. A line with a single remaining cell has an infinite penalty (forced).

### `complete_basis`

```python
complete_basis(C, X) -> Tuple[Set[Tuple[int, int]], int]
```

Positive cells + cheapest zero cells so that the basis is a spanning tree (m+n-1 cells).

### `modi_optimize`

```python
modi_optimize(C, X0, max_iter: int = 10000) -> optiarchitect.core.transportation.TransportSolution
```

MODI (u-v) method with stepping-stone pivots; handles degeneracy.

### `TransportResult`

```python
class TransportResult(C, S, D, dummy, ibfs, start, solution, max_residual)
```

Result of :func:`solve_transportation`.

``C, S, D`` are the *balanced* data actually solved; ``dummy`` is ``None``, ``"source"`` or
``"destination"`` depending on which zero-cost dummy was added; ``ibfs`` maps ``"vam"``,
``"lc"`` and ``"nw"`` to their :class:`IBFS`; ``start`` is the one used; ``solution`` is the
optimal :class:`TransportSolution`; ``max_residual`` is an independent supply/demand check.

### `TransportSolution`

```python
class TransportSolution(X, cost, status, iterations, u, v, delta, basis, zero_cells_added, alternative_optima)
```

Optimal plan found by :func:`modi_optimize`.

Attributes:
    X, cost: allocation matrix and its total cost.
    status: ``"optimal"`` or ``"iteration_limit"``.
    iterations: list of :class:`MODIIteration`.
    u, v: dual potentials; ``delta``: net evaluations (0 on basic cells).
    basis: set of basic cells (a spanning tree of ``m + n - 1`` cells).
    zero_cells_added: number of zero-level cells added to repair degeneracy.
    alternative_optima: ``True`` if a non-basic cell has zero net evaluation.

### `IBFS`

```python
class IBFS(method, X, cost, steps)
```

An initial basic feasible solution: ``method``, allocation matrix ``X``, its ``cost``
and the ordered ``steps`` that produced it.

### `Step`

```python
class Step(kind, cell, qty, cost, penalty)
```

One allocation made while building an initial solution (kind ``"nw"``, ``"lc"`` or ``"vam"``).
``penalty`` is the Vogel penalty and is ``None`` for the other two rules.

### `MODIIteration`

```python
class MODIIteration(entering, delta, theta, leaving, cost_after, loop)
```

One MODI pivot: the ``entering`` cell with its net evaluation ``delta``, the step
``theta``, the ``leaving`` cell, the total cost after the pivot and the stepping-stone ``loop``.

## Assignment (`optiarchitect.core.assignment`)

### `hungarian`

```python
hungarian(C, maximize: bool = False) -> optiarchitect.core.assignment.AssignResult
```

Hungarian algorithm for the assignment problem (row/column reduction + minimum line cover).

Args:
    C: cost (or profit) matrix, 2-D, finite, any shape; a rectangular matrix is padded with
        dummy rows or columns.
    maximize: treat ``C`` as profits to be maximised.

Returns:
    :class:`AssignResult`; its ``cost`` is the total in the original matrix.

Raises:
    ValueError: for an empty, non-2-D or non-finite matrix.

### `AssignResult`

```python
class AssignResult(assignment, unassigned_cols, cost, steps, padded)
```

Result of :func:`hungarian`.

``assignment[i]`` is the column given to original row ``i`` (``None`` if the row got a dummy);
``unassigned_cols`` lists real columns left without a row; ``cost`` is measured in the
*original* matrix; ``steps`` records the method; ``padded`` is ``True`` for rectangular input.

### `AssignStep`

```python
class AssignStep(kind, matrix, matched, delta)
```

One state of the Hungarian method (``kind`` ``"row"``, ``"col"``, ``"adjust"`` or ``"done"``)
with the reduced ``matrix``, the size of the zero matching and the adjustment ``delta``.

## Non-linear optimization (`optiarchitect.core.nlp`)

### `run_method`

```python
run_method(obj: optiarchitect.utils.parser.Objective, name: str, a: float, b: float, x0: float, x1: float, tol: float) -> optiarchitect.core.nlp.OptResult
```

Run one of ``"golden"``, ``"fibonacci"``, ``"newton"`` or ``"secant"`` on an
:class:`~optiarchitect.utils.parser.Objective`.

``x0`` is the Newton start and the first secant point, ``x1`` the second secant point.
Newton and secant use ``min(tol, 1e-8)`` as their tolerance and are told the interval
``[a, b]`` so that an iterate that leaves it is reported (``"left_interval"``).

Raises:
    ValueError: for an unknown method name.

### `diagnose`

```python
diagnose(obj: optiarchitect.utils.parser.Objective, a: float, b: float, x0: float, x1: float) -> Dict[str, Tuple[bool, str, dict]]
```

Applicability of each method: {method: (applicable, reason_code, params)}.
* Bracketing (Golden/Fibonacci) needs f defined on [a, b]; a multimodal sample only triggers a caution.
* Newton needs f''(x0) > 0 (otherwise it is attracted to a maximum / inflection point).
* Secant needs two distinct starting points with a defined f'.

### `golden_section`

```python
golden_section(f, a: float, b: float, tol: float = 1e-06, max_iter: int = 500) -> optiarchitect.core.nlp.OptResult
```

Golden Section search for the minimum of a unimodal ``f`` on ``[a, b]``.

Args:
    f: callable ``f(x) -> float`` (values only; no derivatives needed).
    a, b: finite interval bounds with ``a < b``.
    tol: stop when the bracketing interval is no longer than ``tol``.
    max_iter: iteration cap (reported as status ``"max_iter"``, never hidden).

Returns:
    :class:`OptResult` with ``status`` ``"converged"``, ``"max_iter"`` or ``"domain_error"``.

Raises:
    ValueError: if the interval or the tolerance is invalid.

### `fibonacci_search`

```python
fibonacci_search(f, a: float, b: float, tol: float = 1e-06, n_eval: Optional[int] = None) -> optiarchitect.core.nlp.OptResult
```

Fibonacci search with N function evaluations (+1 to report f at the final point).
Final interval length = 2 L / F_{N+1}, so N is chosen automatically from ``tol``.

### `bisection_search`

```python
bisection_search(f, df, a: float, b: float, tol: float = 1e-06, max_iter: int = 500) -> optiarchitect.core.nlp.OptResult
```

Bisection method applied to f'(x) = 0 on [a, b].

### `newton_raphson`

```python
newton_raphson(f, df, d2f, x0: float, tol: float = 1e-08, a: Optional[float] = None, b: Optional[float] = None, max_iter: int = 100) -> optiarchitect.core.nlp.OptResult
```

Newton's method on f'(x)=0 with safeguards and classification of the stationary point.

### `secant_method`

```python
secant_method(f, df, x0: float, x1: float, tol: float = 1e-08, a: Optional[float] = None, b: Optional[float] = None, max_iter: int = 100, d2f=None) -> optiarchitect.core.nlp.OptResult
```

Secant method applied to f'(x)=0 (needs two distinct starting points).

### `check_unimodality`

```python
check_unimodality(f, a, b) -> bool
```

``True`` if a dense sample of ``f`` on ``[a, b]`` shows no interior peak and at most one
valley (see :func:`check_unimodality_detail` for the reason code).

### `check_unimodality_detail`

```python
check_unimodality_detail(f, a: float, b: float, n: int = 401)
```

Heuristic sampling test (cannot PROVE unimodality). Returns (ok, reason).
reason: unimodal | monotone | flat | multimodal | domain

### `grid_minimum`

```python
grid_minimum(f, a: float, b: float, n: int = 2001) -> Tuple[float, float]
```

Reference scan used as an independent sanity check.

### `OptResult`

```python
class OptResult(method, status, x, fx, iterations, evals, notes, history)
```

Result of a one-variable optimisation method.

All values refer to the internally *minimised* function ``g = sign * f``; use
``Objective.user_value(fx)`` to recover the user's own ``f``.

Attributes:
    method: ``"golden"``, ``"fibonacci"``, ``"newton"`` or ``"secant"``.
    status: ``"converged"``, ``"max_iter"``, ``"zero_curvature"``, ``"not_minimum"``,
        ``"left_interval"``, ``"diverged"`` or ``"domain_error"``.
    x, fx: best point found and the minimised value there (``nan`` on ``domain_error``).
    iterations: iterations performed.
    evals: function evaluations (derivative evaluations for Newton and secant).
    notes: list of ``(code, params)`` remarks, e.g. a boundary or curvature note.
    history: one dict per iteration, used by the step-by-step reports.

## Safe formulas (`optiarchitect.utils.parser`)

### `Objective`

```python
class Objective(text: str, sign: int = 1)
```

Parsed objective g(x) = sign * f(x), with value, first and second derivative.
Derivatives are symbolic when possible, otherwise central finite differences
(``self.symbolic`` tells which).

### `EvalError`

```python
class EvalError(Exception)
```

The function (or a derivative) could not be evaluated at a point.
