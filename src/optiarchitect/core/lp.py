from dataclasses import dataclass, field
from typing import Optional, List, Sequence, Callable
import numpy as np

from optiarchitect.config import EPS, FEAS_TOL, MAX_ITER, BLAND_AFTER, VALID_TYPES

TraceFn = Optional[Callable[[np.ndarray, List[int], List[str], str], None]]


@dataclass
class LPResult:
    """Result of :func:`solve_lp`.

    Attributes:
        status: ``"optimal"``, ``"infeasible"``, ``"unbounded"`` or ``"iteration_limit"``.
        method: ``"standard"``, ``"dual"`` or ``"two_phase"`` (the variant actually used).
        x: optimal point (``None`` unless optimal).
        z: objective value in the *original* sense (max or min), ``None`` unless optimal.
        iterations: simplex pivots performed.
        max_violation: largest violation of any constraint or of ``x >= 0``, computed
            independently of the tableau (``None`` unless optimal).
        var_names: names of the tableau columns.
    """
    status: str                       # optimal | infeasible | unbounded | iteration_limit
    method: str                       # standard | dual | two_phase
    x: Optional[np.ndarray] = None
    z: Optional[float] = None         # objective value in the ORIGINAL sense (max or min)
    iterations: int = 0
    max_violation: Optional[float] = None   # independent feasibility check of x
    var_names: List[str] = field(default_factory=list)


def _validate_lp(c, A, b, con_types, obj_type):
    c = np.asarray(c, dtype=float).ravel()
    A = np.asarray(A, dtype=float)
    if A.ndim == 1:
        A = A.reshape(1, -1)
    b = np.asarray(b, dtype=float).ravel()
    types = list(con_types)
    if obj_type not in ("max", "min"):
        raise ValueError("obj_type must be 'max' or 'min'")
    if c.size < 1 or b.size < 1:
        raise ValueError("At least one variable and one constraint are required")
    if A.ndim != 2 or A.shape != (b.size, c.size) or len(types) != b.size:
        raise ValueError("Inconsistent dimensions of c, A, b, con_types")
    if not (np.isfinite(c).all() and np.isfinite(A).all() and np.isfinite(b).all()):
        raise ValueError("Coefficients must be finite numbers (no NaN/Inf)")
    bad = [t for t in types if t not in VALID_TYPES]
    if bad:
        raise ValueError(f"Invalid constraint type(s): {bad}")
    return c, A, b, types


def choose_method(c_eff: np.ndarray, b: np.ndarray, types: Sequence[str]) -> str:
    """
    Routing rule (c_eff is the objective in 'maximize' form).

    standard  : all rows '<=' and b >= 0         -> slack basis is primal feasible
    dual      : no '=' rows and c_eff <= 0       -> slack basis is DUAL feasible
                (rows '>=' are multiplied by -1; negative RHS is then handled directly)
    two_phase : everything else (equalities, or no dual-feasible start)
    """
    if all(t == "<=" for t in types) and np.all(b >= 0):
        return "standard"
    if "=" not in types and np.all(c_eff <= EPS):
        return "dual"
    return "two_phase"


def lp_applicability(c, b, types, obj) -> dict:
    """Which LP method can start on this model, with the reason (message key)."""
    c = np.asarray(c, float)
    b = np.asarray(b, float)
    c_eff = c if obj == "max" else -c
    std = all(t == "<=" for t in types) and bool(np.all(b >= 0))
    has_eq = "=" in types
    dual_c = bool(np.all(c_eff <= EPS))
    dual = (not has_eq) and dual_c
    return {
        "standard": (std, "lp_r_std_ok" if std else "lp_r_std_no"),
        "dual": (dual, "lp_r_dual_ok" if dual else ("lp_r_dual_eq" if has_eq else "lp_r_dual_c")),
        "two_phase": (True, "lp_r_tp"),
    }


# ---- tableau helpers ------------------------------------------------------
def _pivot(T: np.ndarray, r: int, c: int) -> None:
    T[r, :] /= T[r, c]
    for i in range(T.shape[0]):
        if i != r:
            T[i, :] -= T[i, c] * T[r, :]


def format_tableau(T: np.ndarray, basis: List[int], names: List[str]) -> str:
    head = ["Basic"] + names + ["RHS"]
    rows = [head]
    for i in range(T.shape[0] - 1):
        rows.append([names[basis[i]]] + [f"{v:.4g}" for v in T[i]])
    rows.append(["Z"] + [f"{v:.4g}" for v in T[-1]])
    w = [max(len(r[k]) for r in rows) for k in range(len(head))]
    return "\n".join("  ".join(cell.rjust(w[k]) for k, cell in enumerate(r)) for r in rows)


def _primal(T, basis, allowed, names, trace: TraceFn, title):
    """Primal simplex (maximization form). Dantzig rule, Bland's rule if stalling."""
    m = T.shape[0] - 1
    allowed_mask = np.zeros(T.shape[1] - 1, dtype=bool)
    allowed_mask[list(allowed)] = True
    it, degenerate = 0, 0
    if trace:
        trace(T, basis, names, f"{title} - initial")
    while True:
        red = T[-1, :-1]
        cand = np.where(allowed_mask & (red < -EPS))[0]
        if cand.size == 0:
            return "optimal", it
        if it >= MAX_ITER:
            return "iteration_limit", it
        p_col = cand[0] if degenerate >= BLAND_AFTER else cand[np.argmin(red[cand])]

        col, rhs = T[:m, p_col], T[:m, -1]
        rows = np.where(col > EPS)[0]
        if rows.size == 0:
            return "unbounded", it
        ratios = rhs[rows] / col[rows]
        mn = ratios.min()
        ties = rows[ratios <= mn + 1e-12 * max(1.0, abs(mn))]
        p_row = int(ties[np.argmin([basis[i] for i in ties])])   # Bland tie-break

        degenerate = degenerate + 1 if mn <= EPS else 0
        basis[p_row] = int(p_col)
        _pivot(T, p_row, p_col)
        it += 1
        if trace:
            trace(T, basis, names, f"{title} - iteration {it}")


def _dual(T, basis, names, trace: TraceFn):
    """Dual simplex: requires row 0 >= 0 (dual feasible) on entry."""
    m = T.shape[0] - 1
    it = 0
    if trace:
        trace(T, basis, names, "Dual simplex - initial")
    while True:
        rhs = T[:m, -1]
        if rhs.min() >= -EPS:
            return "optimal", it
        if it >= MAX_ITER:
            return "iteration_limit", it
        p_row = int(np.argmin(rhs))
        row = T[p_row, :-1]
        cand = np.where(row < -EPS)[0]
        if cand.size == 0:
            return "infeasible", it            # dual unbounded <=> primal infeasible
        ratios = np.maximum(T[-1, cand], 0.0) / (-row[cand])
        p_col = int(cand[np.argmin(ratios)])
        basis[p_row] = p_col
        _pivot(T, p_row, p_col)
        it += 1
        if trace:
            trace(T, basis, names, f"Dual simplex - iteration {it}")


def _extract_x(T, basis, n):
    x = np.zeros(n)
    for i, bi in enumerate(basis):
        if bi < n:
            x[bi] = T[i, -1]
    x[np.abs(x) < 1e-10] = 0.0
    return x


def max_violation(A, b, types, x) -> float:
    """Independent check: largest violation of any constraint or of x >= 0."""
    v = float(max(0.0, np.max(-x)))
    for ai, bi, t in zip(A, b, types):
        r = float(ai @ x - bi)
        v = max(v, max(r, 0.0) if t == "<=" else max(-r, 0.0) if t == ">=" else abs(r))
    return v


def _slack_tableau(c_eff, A, b):
    m, n = A.shape
    T = np.zeros((m + 1, n + m + 1))
    T[:m, :n] = A
    T[:m, n:n + m] = np.eye(m)
    T[:m, -1] = b
    T[-1, :n] = -c_eff
    names = [f"x{j+1}" for j in range(n)] + [f"s{i+1}" for i in range(m)]
    return T, list(range(n, n + m)), names


def _two_phase(c_eff, A, b, types, trace: TraceFn):
    m, n = A.shape
    A, b, types = A.copy(), b.copy(), list(types)
    flip = {"<=": ">=", ">=": "<=", "=": "="}
    for i in range(m):                       # make every RHS non-negative
        if b[i] < 0:
            A[i] *= -1.0
            b[i] *= -1.0
            types[i] = flip[types[i]]

    n_slack = sum(t != "=" for t in types)
    n_art = sum(t in (">=", "=") for t in types)
    total = n + n_slack + n_art
    art0 = n + n_slack
    names = ([f"x{j+1}" for j in range(n)] + [f"s{k+1}" for k in range(n_slack)]
             + [f"a{k+1}" for k in range(n_art)])

    T = np.zeros((m + 1, total + 1))
    T[:m, :n] = A
    T[:m, -1] = b
    basis = [0] * m
    s, a = n, art0
    for i, t in enumerate(types):
        if t == "<=":
            T[i, s] = 1.0; basis[i] = s; s += 1
        elif t == ">=":
            T[i, s] = -1.0; s += 1
            T[i, a] = 1.0; basis[i] = a; a += 1
        else:
            T[i, a] = 1.0; basis[i] = a; a += 1

    # ---- Phase I: maximize -sum(artificials) --------------------------
    it1 = 0
    if n_art:
        T[-1, art0:total] = 1.0                       # row0 = -c1, with c1 = -1 on artificials
        for i in range(m):
            if basis[i] >= art0:
                T[-1, :] -= T[i, :]                   # price out basic artificials
        status, it1 = _primal(T, basis, range(art0), names, trace, "Phase I")
        if status == "iteration_limit":
            return status, T, basis, names, it1
        if abs(T[-1, -1]) > FEAS_TOL * (1.0 + np.max(np.abs(b))):
            return "infeasible", T, basis, names, it1

        # drive remaining (zero-level) artificials out of the basis
        redundant = []
        for i in range(m):
            if basis[i] >= art0:
                cols = np.where(np.abs(T[i, :art0]) > 1e-7)[0]
                if cols.size:
                    j = int(cols[np.argmax(np.abs(T[i, cols]))])
                    basis[i] = j
                    _pivot(T, i, j)
                else:
                    redundant.append(i)               # redundant constraint row
        keep = [i for i in range(m) if i not in redundant]
        T = np.vstack([T[keep, :], T[-1:, :]])
        basis = [basis[i] for i in keep]
        T = np.hstack([T[:, :art0], T[:, -1:]])       # drop artificial columns
        names = names[:art0]

    # ---- Phase II --------------------------------------------------------
    T[-1, :] = 0.0
    T[-1, :n] = -c_eff
    for i, bi in enumerate(basis):
        if abs(T[-1, bi]) > 0.0:
            T[-1, :] -= T[-1, bi] * T[i, :]
    status, it2 = _primal(T, basis, range(T.shape[1] - 1), names, trace, "Phase II")
    return status, T, basis, names, it1 + it2


def solve_lp(c, A, b, con_types, obj_type="max", method="auto",
             trace: TraceFn = None) -> LPResult:
    """Solve a linear program with ``x >= 0`` by the standard, dual or two-phase simplex method.

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
    """
    c, A, b, types = _validate_lp(c, A, b, con_types, obj_type)
    m, n = A.shape
    c_eff = c if obj_type == "max" else -c

    auto = choose_method(c_eff, b, types)
    if method == "auto":
        method = auto
    elif method == "standard" and auto != "standard":
        raise ValueError("Standard simplex needs all '<=' rows with b >= 0")
    elif method == "dual" and (("=" in types) or np.any(c_eff > EPS)):
        raise ValueError("Dual simplex needs a dual-feasible start and no '=' rows")
    elif method not in ("standard", "dual", "two_phase"):
        raise ValueError("Unknown method")

    if method in ("standard", "dual"):
        Ad, bd = A.copy(), b.copy()
        for i, t in enumerate(types):
            if t == ">=":                      # a x >= b   <=>   -a x <= -b
                Ad[i] *= -1.0
                bd[i] *= -1.0
        T, basis, names = _slack_tableau(c_eff, Ad, bd)
        if method == "standard":
            status, it = _primal(T, basis, range(T.shape[1] - 1), names, trace, "Simplex")
        else:
            status, it = _dual(T, basis, names, trace)
    else:
        status, T, basis, names, it = _two_phase(c_eff, A, b, types, trace)

    res = LPResult(status=status, method=method, iterations=it, var_names=names)
    if status == "optimal":
        res.x = _extract_x(T, basis, n)
        res.z = float(c @ res.x)
        res.max_violation = max_violation(A, b, types, res.x)
    return res