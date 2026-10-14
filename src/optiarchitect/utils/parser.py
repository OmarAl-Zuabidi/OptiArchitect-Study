# ==========================================================================
#                    SAFE EXPRESSION PARSING + DERIVATIVES
# ==========================================================================
import ast
import math
from typing import Callable
try:                                   # SymPy is needed by Part 3 only
    import sympy as sp
except ImportError:                    # pragma: no cover
    sp = None

# تعريف استثناء خاص بالأخطاء الرياضية
class EvalError(Exception):
    """The function (or a derivative) could not be evaluated at a point."""

_FUNCS = {"sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh",
          "exp", "log", "ln", "sqrt", "abs"}
_CONSTS = {"pi", "E"}
_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd)


def _has_x(node) -> bool:
    return any(isinstance(n, ast.Name) and n.id == "x" for n in ast.walk(node))


def check_expression(text: str) -> str:
    """Whitelist-validate a formula BEFORE it reaches sympy (sympify uses eval)."""
    text = (text or "").strip().replace("^", "**")
    if not text or len(text) > 200:
        raise ValueError("Expression is empty or too long (max 200 characters)")
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError:
        raise ValueError("Syntax error (write products explicitly: 2*x, not 2x)") from None
    for node in ast.walk(tree):
        if isinstance(node, (ast.Expression, ast.Load) + _OPS):
            continue
        if isinstance(node, ast.BinOp) or isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, _OPS):
                raise ValueError("Operator not allowed")
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
                if not _has_x(node.right):          # constant exponent: forbid huge towers like 9**9**9
                    if any(isinstance(n, ast.Pow) for n in ast.walk(node.right)):
                        raise ValueError("Nested constant powers are not allowed")
            continue
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)) or abs(node.value) > 1e6:
                raise ValueError("Only numbers with |value| <= 1e6 are allowed")
            continue
        if isinstance(node, ast.Name):
            if node.id not in _FUNCS | _CONSTS | {"x"}:
                raise ValueError(f"Unknown name '{node.id}' (only x, pi, E and basic functions are allowed)")
            continue
        if isinstance(node, ast.Call):
            if not (isinstance(node.func, ast.Name) and node.func.id in _FUNCS
                    and not node.keywords and len(node.args) == 1):
                raise ValueError("Only one-argument calls of the allowed functions are permitted")
            continue
        raise ValueError(f"Construct not allowed: {type(node).__name__}")
    return text


def _safe(fn: Callable[[float], float]) -> Callable[[float], float]:
    def wrapped(t):
        try:
            v = fn(t)
            v = float(v)
        except (ValueError, ZeroDivisionError, OverflowError, TypeError, NameError, ArithmeticError) as e:
            raise EvalError(str(e)) from None
        if not math.isfinite(v):
            raise EvalError("non-finite value")
        return v
    return wrapped


class Objective:
    """
    Parsed objective g(x) = sign * f(x), with value, first and second derivative.
    Derivatives are symbolic when possible, otherwise central finite differences
    (``self.symbolic`` tells which).
    """

    def __init__(self, text: str, sign: int = 1):
        if sign not in (1, -1):
            raise ValueError("sign must be +1 (minimize f) or -1 (maximize f)")
        self.text, self.sign = text, sign
        if sp is None:
            raise RuntimeError("SymPy is required for Part 3 (pip install sympy)")
        clean = check_expression(text)
        X = sp.Symbol("x")
        local = {"x": X, "pi": sp.pi, "E": sp.E, "ln": sp.log, "log": sp.log, "exp": sp.exp,
                 "sqrt": sp.sqrt, "abs": sp.Abs, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
                 "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
                 "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh}
        try:
            expr = sp.sympify(clean, locals=local)
        except Exception as e:
            raise ValueError(f"Cannot parse expression: {e}") from None
        if expr.free_symbols - {X}:
            raise ValueError("Only the variable x is allowed")
        self.expr = expr
        g = sign * expr
        mods = [{"sign": lambda v: (v > 0) - (v < 0)}, "math"]

        def lam(e):
            return _safe(sp.lambdify(X, e, mods))

        self.f = lam(g)
        d1, d2 = sp.diff(g, X), None
        self.symbolic = True
        try:
            if d1.has(sp.DiracDelta, sp.Heaviside):
                raise ValueError
            self.df = lam(d1)
            d2 = sp.diff(d1, X)
        except Exception:
            self.symbolic = False
            self.df = lambda t: (self.f(t + _h(t)) - self.f(t - _h(t))) / (2 * _h(t))
        try:
            if d2 is None or d2.has(sp.DiracDelta, sp.Heaviside):
                raise ValueError
            self.d2f = lam(d2)
        except Exception:
            self.symbolic = False
            self.d2f = lambda t: (self.df(t + _h(t, 1e-4)) - self.df(t - _h(t, 1e-4))) / (2 * _h(t, 1e-4))
        self.df_text = sp.sstr(sp.diff(expr, X))
        self.d2f_text = sp.sstr(sp.diff(expr, X, 2))

    def user_value(self, gx: float) -> float:
        """Value of the user's f from the internally minimized g."""
        return self.sign * gx


def _h(t: float, rel: float = 1e-5) -> float:
    return rel * max(1.0, abs(t))