import math
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple

from optiarchitect.config import EPS, CURV_TOL, SQRT_EPS
from optiarchitect.utils.parser import EvalError, Objective, _h

# ==========================================================================
@dataclass
class OptResult:
    """Result of a one-variable optimisation method.

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
    """
    method: str                         # golden | fibonacci | newton | secant
    status: str                         # converged | max_iter | zero_curvature | not_minimum |
                                        # left_interval | diverged | domain_error
    x: float
    fx: float                           # minimized value g(x)
    iterations: int
    evals: int                          # function evaluations (or derivative evaluations for newton/secant)
    notes: List[Tuple[str, dict]] = field(default_factory=list)
    history: List[dict] = field(default_factory=list)

    @property
    def func_evals(self) -> int:          # alias kept for backward compatibility
        return self.evals


def _counted(fn):
    cnt = [0]

    def w(t):
        cnt[0] += 1
        return fn(t)
    return w, cnt


def _check_interval(a, b, tol):
    if not (math.isfinite(a) and math.isfinite(b) and a < b):
        raise ValueError("Need finite a < b")
    if not (math.isfinite(tol) and tol > 0):
        raise ValueError("Tolerance must be a positive finite number")


def _bracket_notes(x, a0, b0, tol) -> List[Tuple[str, dict]]:
    notes = []
    if tol < SQRT_EPS * max(1.0, abs(x)):
        notes.append(("precision", {"limit": SQRT_EPS * max(1.0, abs(x))}))
    if min(abs(x - a0), abs(x - b0)) <= tol:
        notes.append(("endpoint", {}))
    return notes


def check_unimodality_detail(f, a: float, b: float, n: int = 401):
    """
    Heuristic sampling test (cannot PROVE unimodality). Returns (ok, reason).
    reason: unimodal | monotone | flat | multimodal | domain
    """
    step = (b - a) / (n - 1)
    try:
        vals = [f(a + i * step) for i in range(n)]
    except EvalError:
        return False, "domain"
    scale = max(abs(v) for v in vals)
    if scale == 0.0:
        return True, "flat"
    thr = 1e-12 * scale                       # RELATIVE threshold (the original used an absolute 1e-10)
    signs = []
    for i in range(n - 1):
        d = vals[i + 1] - vals[i]
        if abs(d) > thr:
            signs.append(1 if d > 0 else -1)
    if not signs:
        return True, "flat"
    peaks = sum(1 for i in range(len(signs) - 1) if signs[i] > 0 and signs[i + 1] < 0)
    valleys = sum(1 for i in range(len(signs) - 1) if signs[i] < 0 and signs[i + 1] > 0)
    if peaks == 0 and valleys <= 1:
        return True, ("unimodal" if valleys == 1 else "monotone")
    return False, "multimodal"


def check_unimodality(f, a, b) -> bool:
    """``True`` if a dense sample of ``f`` on ``[a, b]`` shows no interior peak and at most one
    valley (see :func:`check_unimodality_detail` for the reason code).
    """
    return check_unimodality_detail(f, a, b)[0]


def grid_minimum(f, a: float, b: float, n: int = 2001) -> Tuple[float, float]:
    """Reference scan used as an independent sanity check."""
    best = (math.nan, math.inf)
    for i in range(n):
        x = a + (b - a) * i / (n - 1)
        try:
            v = f(x)
        except EvalError:
            continue
        if v < best[1]:
            best = (x, v)
    return best


# ==========================================================================
#                           BRACKETING METHODS
# ==========================================================================
def golden_section(f, a: float, b: float, tol: float = 1e-6, max_iter: int = 500) -> OptResult:
    """Golden Section search for the minimum of a unimodal ``f`` on ``[a, b]``.

    Args:
        f: callable ``f(x) -> float`` (values only; no derivatives needed).
        a, b: finite interval bounds with ``a < b``.
        tol: stop when the bracketing interval is no longer than ``tol``.
        max_iter: iteration cap (reported as status ``"max_iter"``, never hidden).

    Returns:
        :class:`OptResult` with ``status`` ``"converged"``, ``"max_iter"`` or ``"domain_error"``.

    Raises:
        ValueError: if the interval or the tolerance is invalid.
    """
    _check_interval(a, b, tol)
    a0, b0 = a, b
    g, cnt = _counted(f)
    r = (math.sqrt(5) - 1) / 2
    hist, k = [], 0
    try:
        x1, x2 = b - r * (b - a), a + r * (b - a)
        f1, f2 = g(x1), g(x2)
        while (b - a) > tol and k < max_iter:
            k += 1
            hist.append(dict(k=k, a=a, b=b, x1=x1, x2=x2, f1=f1, f2=f2))
            if f1 < f2:
                b, x2, f2 = x2, x1, f1
                x1 = b - r * (b - a)
                f1 = g(x1)
            else:
                a, x1, f1 = x1, x2, f2
                x2 = a + r * (b - a)
                f2 = g(x2)
        x = (a + b) / 2
        fx = g(x)
    except EvalError:
        return OptResult("golden", "domain_error", math.nan, math.nan, k, cnt[0], [("domain", {})], hist)
    status = "converged" if (b - a) <= tol else "max_iter"
    return OptResult("golden", status, x, fx, k, cnt[0], _bracket_notes(x, a0, b0, tol), hist)


def fibonacci_search(f, a: float, b: float, tol: float = 1e-6, n_eval: Optional[int] = None) -> OptResult:
    """
    Fibonacci search with N function evaluations (+1 to report f at the final point).
    Final interval length = 2 L / F_{N+1}, so N is chosen automatically from ``tol``.
    """
    _check_interval(a, b, tol)
    a0, b0, L = a, b, b - a
    fib = [1, 1]

    def grow(upto):
        while len(fib) <= upto:
            fib.append(fib[-1] + fib[-2])

    if n_eval is None:
        N = 2
        grow(N + 1)
        while 2 * L / fib[N + 1] > tol and N < 90:
            N += 1
            grow(N + 1)
    else:
        if int(n_eval) != n_eval or n_eval < 2:
            raise ValueError("n_eval must be an integer >= 2")
        N = int(n_eval)
        grow(N + 1)
    F = fib[N + 1]
    g, cnt = _counted(f)
    hist = []
    try:
        x1, x2 = a + fib[N - 1] / F * L, a + fib[N] / F * L
        f1, f2 = g(x1), g(x2)
        for k in range(1, N - 1):                      # k = 1 .. N-2 : one new evaluation each
            hist.append(dict(k=k, a=a, b=b, x1=x1, x2=x2, f1=f1, f2=f2))
            if f1 < f2:
                b, x2, f2 = x2, x1, f1
                x1 = a + fib[N - k - 1] / F * L
                f1 = g(x1)
            else:
                a, x1, f1 = x1, x2, f2
                x2 = a + fib[N - k] / F * L
                f2 = g(x2)
        hist.append(dict(k=N - 1, a=a, b=b, x1=x1, x2=x2, f1=f1, f2=f2))
        if f1 < f2:                                    # last comparison: no new evaluation needed
            b = x2
        else:
            a = x1
        x = (a + b) / 2
        fx = g(x)
    except EvalError:
        return OptResult("fibonacci", "domain_error", math.nan, math.nan, 0, cnt[0], [("domain", {})], hist)
    notes = _bracket_notes(x, a0, b0, tol)
    notes.append(("fib_n", {"n": N}))
    return OptResult("fibonacci", "converged", x, fx, N - 1, cnt[0], notes, hist)


def bisection_search(f, df, a: float, b: float, tol: float = 1e-6, max_iter: int = 500) -> OptResult:
    """Bisection method applied to f'(x) = 0 on [a, b]."""
    _check_interval(a, b, tol)
    a0, b0 = a, b
    cnt = [0]
    def d(t):
        cnt[0] += 1
        res = df(t)
        if not math.isfinite(res):
            raise EvalError("Domain error")
        return res

    hist, k = [], 0
    try:
        da, db = d(a), d(b)
        if da * db > 0:
            return OptResult("bisection", "no_bracket", math.nan, math.nan, 0, cnt[0], [("no_bracket", {})], [])

        while (b - a) > tol and k < max_iter:
            k += 1
            mid = (a + b) / 2.0
            dm = d(mid)
            hist.append(dict(k=k, a=a, b=b, mid=mid, d_mid=dm))
            if abs(dm) <= EPS:
                a = b = mid
                break
            if da * dm < 0:
                b = mid
                db = dm
            else:
                a = mid
                da = dm
        x = (a + b) / 2.0
        fx = f(x)
    except EvalError:
        return OptResult("bisection", "domain_error", math.nan, math.nan, k, cnt[0], [("domain", {})], hist)

    status = "converged" if (b - a) <= tol or abs(da) <= EPS or abs(db) <= EPS else "max_iter"
    return OptResult("bisection", status, x, fx, k, cnt[0], _bracket_notes(x, a0, b0, tol), hist)


# ==========================================================================
#                          DERIVATIVE-BASED METHODS
# ==========================================================================
def _classify(d2: float) -> Optional[str]:
    """None if the stationary point is a local minimum, otherwise a note code."""
    if d2 > CURV_TOL:
        return None
    return "maximum" if d2 < -CURV_TOL else "inflection"


def newton_raphson(f, df, d2f, x0: float, tol: float = 1e-8, a: Optional[float] = None,
                   b: Optional[float] = None, max_iter: int = 100) -> OptResult:
    """Newton's method on f'(x)=0 with safeguards and classification of the stationary point."""
    if not (math.isfinite(x0) and math.isfinite(tol) and tol > 0):
        raise ValueError("x0 must be finite and tol > 0")
    cnt, x, hist, k = [0], x0, [], 0

    def counted(fn):
        def w(t):
            cnt[0] += 1
            res = fn(t)
            if not math.isfinite(res):
                raise ValueError("Domain or non-finite error")
            return res
        return w

    dfc, d2c = counted(df), counted(d2f)

    def finish(status, notes=()):
        try:
            fx = f(x)
            if not math.isfinite(fx):
                fx = math.nan
        except (EvalError, ValueError, ArithmeticError):
            fx = math.nan
        return OptResult("newton", status, x, fx, k, cnt[0], list(notes), hist)

    # 1. فحص مجال الدالة الأساسية عند نقطة البداية (Domain Check)
    try:
        fx0 = f(x0)
        if not math.isfinite(fx0):
            return finish("domain_error", [("domain", {})])
    except (EvalError, ValueError, ArithmeticError):
        return finish("domain_error", [("domain", {})])

    try:
        while k < max_iter:
            g1, g2 = dfc(x), d2c(x)
            hist.append(dict(k=k, x=x, d1=g1, d2=g2))

            if abs(g2) <= CURV_TOL * max(1.0, abs(g1)):
                return finish("zero_curvature", [("zero_curvature", {})])

            if abs(g1) <= tol:
                note = _classify(g2)
                return finish("converged" if note is None else "not_minimum",
                              [] if note is None else [(note, {})])

            xn = x - g1 / g2
            k += 1

            if (a is not None and xn < a) or (b is not None and xn > b):
                return finish("left_interval", [("left_interval", {"x": xn})])

            if abs(xn) > 1e12:
                return finish("diverged", [("diverged", {})])

            step = abs(xn - x)
            x = xn

            # فحص مجال الدالة عند النقطة الجديدة
            try:
                if not math.isfinite(f(x)):
                    return finish("domain_error", [("domain", {})])
            except (EvalError, ValueError, ArithmeticError):
                return finish("domain_error", [("domain", {})])

            if step <= tol * (1.0 + abs(x)):
                g1, g2 = dfc(x), d2c(x)
                hist.append(dict(k=k, x=x, d1=g1, d2=g2))
                if abs(g2) <= CURV_TOL * max(1.0, abs(g1)):
                    return finish("zero_curvature", [("zero_curvature", {})])
                note = _classify(g2)
                return finish("converged" if note is None else "not_minimum",
                              [] if note is None else [(note, {})])

        return finish("max_iter")

    except (EvalError, ValueError, ArithmeticError):
        return finish("domain_error", [("domain", {})])


def secant_method(f, df, x0: float, x1: float, tol: float = 1e-8, a: Optional[float] = None,
                  b: Optional[float] = None, max_iter: int = 100, d2f=None) -> OptResult:
    """Secant method applied to f'(x)=0 (needs two distinct starting points)."""
    if not (math.isfinite(x0) and math.isfinite(x1) and x0 != x1 and math.isfinite(tol) and tol > 0):
        raise ValueError("Need two distinct finite starting points and tol > 0")
    cnt, hist, k = [0], [], 0
    xp, xc = x0, x1

    def d(t):
        cnt[0] += 1
        return df(t)

    def curvature(t):
        if d2f is not None:
            return d2f(t)
        h = _h(t)
        return (df(t + h) - df(t - h)) / (2 * h)

    def finish(status, notes=()):
        try:
            fx = f(xc)
        except EvalError:
            fx = math.nan
        return OptResult("secant", status, xc, fx, k, cnt[0], list(notes), hist)

    def converged():
        note = _classify(curvature(xc))
        return finish("converged" if note is None else "not_minimum", [] if note is None else [(note, {})])

    try:
        gp, gc = d(xp), d(xc)
        while k < max_iter:
            hist.append(dict(k=k, x_prev=xp, x=xc, d1=gc))
            if abs(gc) <= tol:
                return converged()
            den = gc - gp
            if den == 0.0 or abs(den) <= 1e-300:
                return finish("zero_curvature", [("zero_curvature", {})])
            xn = xc - gc * (xc - xp) / den
            k += 1
            if (a is not None and xn < a) or (b is not None and xn > b):
                return finish("left_interval", [("left_interval", {"x": xn})])
            if abs(xn) > 1e12 or not math.isfinite(xn):
                return finish("diverged", [("diverged", {})])
            step = abs(xn - xc)
            xp, gp = xc, gc
            xc, gc = xn, d(xn)
            if step <= tol * (1.0 + abs(xc)) or abs(gc) <= tol:
                hist.append(dict(k=k, x_prev=xp, x=xc, d1=gc))
                return converged()
        return finish("max_iter")
    except EvalError:
        return finish("domain_error", [("domain", {})])




# ==========================================================================
#                              DIAGNOSIS
# ==========================================================================
def diagnose(obj: Objective, a: float, b: float, x0: float, x1: float) -> Dict[str, Tuple[bool, str, dict]]:
    """
    Applicability of each method: {method: (applicable, reason_code, params)}.
    * Bracketing (Golden/Fibonacci) needs f defined on [a, b]; a multimodal sample only triggers a caution.
    * Newton needs f''(x0) > 0 (otherwise it is attracted to a maximum / inflection point).
    * Secant needs two distinct starting points with a defined f'.
    """
    ok, why = check_unimodality_detail(obj.f, a, b)
    out: Dict[str, Tuple[bool, str, dict]] = {}
    for m in ("golden", "fibonacci"):
        out[m] = (why != "domain", "uni_" + why, {})
    try:
        c0 = obj.d2f(x0)
    except EvalError:
        c0 = math.nan
    if math.isnan(c0):
        out["newton"] = (False, "deriv_fail", {})
    elif c0 > CURV_TOL:
        out["newton"] = (True, "newton_ok", {"v": c0})
    else:
        out["newton"] = (False, "newton_curv", {"v": c0})
    try:
        if x0 == x1:
            out["secant"] = (False, "secant_same", {})
        else:
            obj.df(x0), obj.df(x1)
            out["secant"] = (True, "secant_ok", {})
    except EvalError:
        out["secant"] = (False, "deriv_fail", {})
    return out


def run_method(obj: Objective, name: str, a: float, b: float, x0: float, x1: float, tol: float) -> OptResult:
    """Run one of ``"golden"``, ``"fibonacci"``, ``"newton"`` or ``"secant"`` on an
    :class:`~optiarchitect.utils.parser.Objective`.

    ``x0`` is the Newton start and the first secant point, ``x1`` the second secant point.
    Newton and secant use ``min(tol, 1e-8)`` as their tolerance and are told the interval
    ``[a, b]`` so that an iterate that leaves it is reported (``"left_interval"``).

    Raises:
        ValueError: for an unknown method name.
    """
    if name == "golden":
        return golden_section(obj.f, a, b, tol)
    if name == "fibonacci":
        return fibonacci_search(obj.f, a, b, tol)
    if name == "newton":
        return newton_raphson(obj.f, obj.df, obj.d2f, x0, min(tol, 1e-8), a, b)
    if name == "secant":
        return secant_method(obj.f, obj.df, x0, x1, min(tol, 1e-8), a, b, d2f=obj.d2f)
    raise ValueError("unknown method")
