from dataclasses import dataclass
from collections import deque
from typing import List, Tuple, Set, Dict, Optional
import numpy as np

from optiarchitect.config import TOL, Cell


# ==========================================================================
#                         TRANSPORTATION: CORE
# ==========================================================================

@dataclass
class Step:
    """One allocation made while building an initial solution (kind ``"nw"``, ``"lc"`` or ``"vam"``).
    ``penalty`` is the Vogel penalty and is ``None`` for the other two rules.
    """
    kind: str                 # 'nw' | 'lc' | 'vam'
    cell: Cell
    qty: float
    cost: float
    penalty: Optional[float] = None


@dataclass
class IBFS:
    """An initial basic feasible solution: ``method``, allocation matrix ``X``, its ``cost``
    and the ordered ``steps`` that produced it.
    """
    method: str
    X: np.ndarray
    cost: float
    steps: List[Step]


@dataclass
class MODIIteration:
    """One MODI pivot: the ``entering`` cell with its net evaluation ``delta``, the step
    ``theta``, the ``leaving`` cell, the total cost after the pivot and the stepping-stone ``loop``.
    """
    entering: Cell
    delta: float
    theta: float
    leaving: Cell
    cost_after: float
    loop: List[Cell]


@dataclass
class TransportSolution:
    """Optimal plan found by :func:`modi_optimize`.

    Attributes:
        X, cost: allocation matrix and its total cost.
        status: ``"optimal"`` or ``"iteration_limit"``.
        iterations: list of :class:`MODIIteration`.
        u, v: dual potentials; ``delta``: net evaluations (0 on basic cells).
        basis: set of basic cells (a spanning tree of ``m + n - 1`` cells).
        zero_cells_added: number of zero-level cells added to repair degeneracy.
        alternative_optima: ``True`` if a non-basic cell has zero net evaluation.
    """
    X: np.ndarray
    cost: float
    status: str                       # optimal | iteration_limit
    iterations: List[MODIIteration]
    u: np.ndarray
    v: np.ndarray
    delta: np.ndarray                 # net evaluations (0 on basic cells)
    basis: Set[Cell]
    zero_cells_added: int             # degeneracy repairs
    alternative_optima: bool


@dataclass
class TransportResult:
    """Result of :func:`solve_transportation`.

    ``C, S, D`` are the *balanced* data actually solved; ``dummy`` is ``None``, ``"source"`` or
    ``"destination"`` depending on which zero-cost dummy was added; ``ibfs`` maps ``"vam"``,
    ``"lc"`` and ``"nw"`` to their :class:`IBFS`; ``start`` is the one used; ``solution`` is the
    optimal :class:`TransportSolution`; ``max_residual`` is an independent supply/demand check.
    """
    C: np.ndarray                     # balanced data actually solved
    S: np.ndarray
    D: np.ndarray
    dummy: Optional[str]              # None | 'source' | 'destination'
    ibfs: Dict[str, IBFS]
    start: str
    solution: TransportSolution
    max_residual: float               # independent feasibility check


def _validate_transport(C, S, D):
    C = np.asarray(C, dtype=float)
    S = np.asarray(S, dtype=float).ravel()
    D = np.asarray(D, dtype=float).ravel()
    if C.ndim != 2 or S.size < 1 or D.size < 1 or C.shape != (S.size, D.size):
        raise ValueError("Inconsistent dimensions of C, S, D")
    if not (np.isfinite(C).all() and np.isfinite(S).all() and np.isfinite(D).all()):
        raise ValueError("All data must be finite numbers (no NaN/Inf)")
    if (S < 0).any() or (D < 0).any():
        raise ValueError("Supply and demand must be non-negative")
    if S.sum() <= 0 or D.sum() <= 0:
        raise ValueError("Total supply and total demand must be positive")
    return C, S, D


def balance_transport(C, S, D):
    """Add a zero-cost dummy source/destination if needed (tolerant comparison)."""
    ts, td = float(S.sum()), float(D.sum())
    if abs(ts - td) <= TOL * max(ts, td):
        return C, S, D, None
    if ts < td:
        return (np.vstack([C, np.zeros((1, C.shape[1]))]), np.append(S, td - ts), D, "source")
    return (np.hstack([C, np.zeros((C.shape[0], 1))]), S, np.append(D, ts - td), "destination")


def _allocate(S, D, X, r, c, tol):
    q = min(S[r], D[c])
    X[r, c] = q
    S[r] -= q
    D[c] -= q
    if S[r] <= tol:
        S[r] = 0.0
    if D[c] <= tol:
        D[c] = 0.0
    return q


def northwest_corner(C, S, D) -> IBFS:
    """North-West Corner rule on balanced data; returns an :class:`IBFS`.
    """
    m, n = C.shape
    S, D, X = S.astype(float).copy(), D.astype(float).copy(), np.zeros((m, n))
    tol = TOL * max(1.0, S.sum())
    steps, i, j = [], 0, 0
    while i < m and j < n:
        if S[i] <= tol:
            i += 1; continue                      # skip exhausted rows
        if D[j] <= tol:
            j += 1; continue
        q = _allocate(S, D, X, i, j, tol)
        steps.append(Step("nw", (i, j), q, C[i, j]))
    return IBFS("nw", X, float(np.sum(C * X)), steps)


def least_cost(C, S, D) -> IBFS:
    """Least Cost rule on balanced data (ties go to the larger shipment); returns an :class:`IBFS`.
    """
    m, n = C.shape
    S, D, X = S.astype(float).copy(), D.astype(float).copy(), np.zeros((m, n))
    tol = TOL * max(1.0, S.sum())
    ar, ac, steps = S > tol, D > tol, []
    while ar.any() and ac.any():
        M = np.where(np.outer(ar, ac), C, np.inf)
        cand = np.argwhere(M == M.min())
        r, c = max(cand, key=lambda rc: min(S[rc[0]], D[rc[1]]))   # tie -> larger shipment
        q = _allocate(S, D, X, r, c, tol)
        steps.append(Step("lc", (int(r), int(c)), q, C[r, c]))
        ar[r] = S[r] > tol
        ac[c] = D[c] > tol
    return IBFS("lc", X, float(np.sum(C * X)), steps)


def vogel(C, S, D) -> IBFS:
    """VAM. A line with a single remaining cell has an infinite penalty (forced)."""
    m, n = C.shape
    S, D, X = S.astype(float).copy(), D.astype(float).copy(), np.zeros((m, n))
    tol = TOL * max(1.0, S.sum())
    ar, ac, steps = S > tol, D > tol, []
    while ar.any() and ac.any():
        rows, cols = np.where(ar)[0], np.where(ac)[0]
        sub = C[np.ix_(rows, cols)]
        if cols.size == 1:
            rp = np.full(rows.size, np.inf)
        else:
            s = np.sort(sub, axis=1); rp = s[:, 1] - s[:, 0]
        if rows.size == 1:
            cp = np.full(cols.size, np.inf)
        else:
            s = np.sort(sub, axis=0); cp = s[1, :] - s[0, :]
        pmax = max(rp.max(), cp.max())
        cands = []
        for k in np.where(rp >= pmax - 1e-12)[0]:
            cands.append((sub[k, np.argmin(sub[k])], int(rows[k]), int(cols[np.argmin(sub[k])])))
        for k in np.where(cp >= pmax - 1e-12)[0]:
            cands.append((sub[np.argmin(sub[:, k]), k], int(rows[np.argmin(sub[:, k])]), int(cols[k])))
        cands.sort(key=lambda t: (t[0], -min(S[t[1]], D[t[2]]), t[1], t[2]))
        _, r, c = cands[0]
        q = _allocate(S, D, X, r, c, tol)
        steps.append(Step("vam", (r, c), q, C[r, c], float(pmax)))
        ar[r] = S[r] > tol
        ac[c] = D[c] > tol
    return IBFS("vam", X, float(np.sum(C * X)), steps)


def complete_basis(C, X) -> Tuple[Set[Cell], int]:
    """Positive cells + cheapest zero cells so that the basis is a spanning tree (m+n-1 cells)."""
    m, n = C.shape
    parent = list(range(m + n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    basis: Set[Cell] = set()
    for i, j in np.argwhere(X > 1e-12):
        ri, rj = find(int(i)), find(m + int(j))
        if ri == rj:
            raise ValueError("Positive cells contain a cycle - not a basic solution")
        parent[ri] = rj
        basis.add((int(i), int(j)))
    added = 0
    order = sorted(((C[i, j], i, j) for i in range(m) for j in range(n) if (i, j) not in basis))
    for _, i, j in order:
        if len(basis) == m + n - 1:
            break
        ri, rj = find(i), find(m + j)
        if ri != rj:
            parent[ri] = rj
            basis.add((i, j))
            added += 1
    return basis, added


def _adjacency(basis: Set[Cell], m: int, n: int):
    adj = [[] for _ in range(m + n)]
    for i, j in basis:
        adj[i].append(m + j)
        adj[m + j].append(i)
    return adj


def _potentials(C, basis, m, n):
    adj = _adjacency(basis, m, n)
    pot = np.full(m + n, np.nan)
    pot[0] = 0.0
    dq = deque([0])
    while dq:
        a = dq.popleft()
        for b in adj[a]:
            if np.isnan(pot[b]):
                i, j = (a, b - m) if a < m else (b, a - m)
                pot[b] = C[i, j] - pot[a]                # u_i + v_j = c_ij on basic cells
                dq.append(b)
    return pot[:m], pot[m:]


def _tree_path(basis, m, n, i, j) -> List[Cell]:
    """Cells on the unique tree path from row i to column j."""
    adj = _adjacency(basis, m, n)
    prev = {i: None}
    dq = deque([i])
    while dq:
        a = dq.popleft()
        if a == m + j:
            break
        for b in adj[a]:
            if b not in prev:
                prev[b] = a
                dq.append(b)
    nodes, a = [], m + j
    while a is not None:
        nodes.append(a)
        a = prev[a]
    nodes.reverse()
    return [((p, q - m) if p < m else (q, p - m)) for p, q in zip(nodes, nodes[1:])]


def modi_optimize(C, X0, max_iter: int = 10_000) -> TransportSolution:
    """MODI (u-v) method with stepping-stone pivots; handles degeneracy."""
    C = np.asarray(C, float)
    m, n = C.shape
    X = np.array(X0, float)
    basis, added = complete_basis(C, X)
    tol = TOL * max(1.0, float(np.abs(C).max()))
    history: List[MODIIteration] = []
    status = "optimal"
    while True:
        u, v = _potentials(C, basis, m, n)
        delta = C - u[:, None] - v[None, :]
        masked = delta.copy()
        for cell in basis:
            masked[cell] = np.inf
            delta[cell] = 0.0
        i, j = np.unravel_index(np.argmin(masked), masked.shape)
        i, j = int(i), int(j)
        if masked[i, j] >= -tol:
            break
        if len(history) >= max_iter:
            status = "iteration_limit"
            break
        path = _tree_path(basis, m, n, i, j)
        minus, plus = path[0::2], path[1::2]
        theta = min(X[c] for c in minus)
        leaving = min(c for c in minus if X[c] <= theta + 1e-12)      # Bland-like tie-break
        for c in plus:
            X[c] += theta
        for c in minus:
            X[c] -= theta
        X[i, j] = theta
        X[leaving] = 0.0
        X[np.abs(X) < 1e-12] = 0.0
        basis.remove(leaving)
        basis.add((i, j))
        history.append(MODIIteration((i, j), float(masked[i, j]), float(theta), leaving,
                                     float(np.sum(C * X)), [(i, j)] + path))
    nonbasic = np.ones((m, n), dtype=bool)
    for cell in basis:
        nonbasic[cell] = False
    alt = bool(np.any(nonbasic & (np.abs(delta) <= tol)))
    return TransportSolution(X, float(np.sum(C * X)), status, history, u, v, delta, basis, added, alt)


def solve_transportation(C, S, D, start: str = "best") -> TransportResult:
    """Solve a transportation problem: validate, balance, build the three starting solutions, optimise.

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
    """
    C, S, D = _validate_transport(C, S, D)
    Cb, Sb, Db, dummy = balance_transport(C, S, D)
    ibfs = {"vam": vogel(Cb, Sb, Db), "lc": least_cost(Cb, Sb, Db), "nw": northwest_corner(Cb, Sb, Db)}
    if start == "best":
        start = min(ibfs, key=lambda k: ibfs[k].cost)     # ties prefer VAM
    elif start not in ibfs:
        raise ValueError("start must be 'best', 'vam', 'lc' or 'nw'")
    sol = modi_optimize(Cb, ibfs[start].X)
    res = float(max(np.max(np.abs(sol.X.sum(1) - Sb)), np.max(np.abs(sol.X.sum(0) - Db)),
                    max(0.0, -sol.X.min())))
    return TransportResult(Cb, Sb, Db, dummy, ibfs, start, sol, res)