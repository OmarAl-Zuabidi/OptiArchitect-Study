import math
from itertools import combinations
from typing import Optional

import numpy as np

from optiarchitect.config import EPS
from optiarchitect.utils.text_fix import fix_ar
from optiarchitect.utils.parser import Objective


def _vertices(cons):
    pts = []
    for (a1, a2, r1), (d1, d2, r2) in combinations([(p[0], p[1], p[2]) for p in cons], 2):
        det = a1 * d2 - a2 * d1
        if abs(det) < EPS:
            continue
        p = np.array([(r1 * d2 - a2 * r2) / det, (a1 * r2 - r1 * d1) / det])
        if all(_sat(p, q) for q in cons):
            if not any(np.allclose(p, u, atol=1e-8) for u in pts):
                pts.append(p)
    return pts


def _sat(p, con):
    a1, a2, r, t = con
    v = a1 * p[0] + a2 * p[1] - r
    tol = 1e-7 * (1.0 + abs(r))
    return v <= tol if t == "<=" else v >= -tol if t == ">=" else abs(v) <= tol


def plot_feasible_region(c, A, b, con_types, obj_type="max", result=None,
                         lang="en", title="", labels=("x1", "x2"), show=True,
                         save_path=None, return_fig=False):
    """Shaded feasible region, constraint lines, optimum and iso-objective line (n = 2).

    ``return_fig=True`` hands the matplotlib Figure back to the caller (used by the
    web app) instead of showing/closing it.
    """
    import matplotlib.pyplot as plt
    from optiarchitect.core.lp import _validate_lp

    c, A, b, types = _validate_lp(c, A, b, con_types, obj_type)
    if A.shape[1] != 2:
        raise ValueError("The graphical method requires exactly 2 decision variables")
    tx = fix_ar if lang == "ar" else (lambda s: s)

    cons = [(A[i, 0], A[i, 1], b[i], types[i]) for i in range(len(b))]
    axes_c = [(1.0, 0.0, 0.0, ">="), (0.0, 1.0, 0.0, ">=")]
    base = _vertices(cons + axes_c)
    top = max((float(np.max(p)) for p in base), default=0.0)
    L = 1.3 * top if top > 0 else 10.0
    box = [(1.0, 0.0, L, "<="), (0.0, 1.0, L, "<=")]
    poly = _vertices(cons + axes_c + box)

    fig, ax = plt.subplots(num="OptiArchitect - Linear Programming")
    if len(poly) >= 3:
        ctr = np.mean(poly, axis=0)
        poly.sort(key=lambda p: math.atan2(p[1] - ctr[1], p[0] - ctr[0]))
        P = np.array(poly)
        ax.fill(P[:, 0], P[:, 1], alpha=0.25, label=tx("Feasible" if lang == "en" else "منطقة الحلول الممكنة"))

    xs = np.linspace(0, L, 200)
    for i, (a1, a2, r, t) in enumerate(cons):
        if abs(a2) > EPS:
            ax.plot(xs, (r - a1 * xs) / a2, label=f"C{i+1}: {a1:g}*x1 + {a2:g}*x2 {t} {r:g}")
        elif abs(a1) > EPS:
            ax.axvline(r / a1, label=f"C{i+1}: {a1:g}*x1 + {a2:g}*x2 {t} {r:g}")

    if result is not None and getattr(result, "status", None) == "optimal":
        xo = result.x
        ax.plot(*xo, marker="*", ms=16, color="k", ls="none", label=f"x* = ({xo[0]:.4g}, {xo[1]:.4g})")
        if abs(c[1]) > EPS:
            ax.plot(xs, (c @ xo - c[0] * xs) / c[1], "k--", lw=1, label="Z")
        elif abs(c[0]) > EPS:
            ax.axvline(xo[0], color="k", ls="--", lw=1, label="Z")

    ax.set_xlim(0, L); ax.set_ylim(0, L)
    ax.set_xlabel(tx(labels[0])); ax.set_ylabel(tx(labels[1])); ax.set_title(tx(title))
    ax.grid(True)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
    if return_fig:
        return fig
    if show:
        plt.show()
    plt.close(fig)


def plot_nlp_1d(obj: Objective, a: float, b: float, x_star: Optional[float] = None,
                lang: str = "en", title: str = "", show: bool = True,
                save_path: Optional[str] = None, return_fig: bool = False):
    """Plots the USER's f(x) (not the internally minimized g = sign*f) over [a, b]."""
    import matplotlib.pyplot as plt
    tx = fix_ar if lang == "ar" else (lambda s: s)

    xs = np.linspace(a, b, 400)
    ys = []
    for x in xs:
        try:
            ys.append(obj.user_value(obj.f(float(x))))
        except Exception:
            ys.append(math.nan)          # undefined points are left as gaps

    fig, ax = plt.subplots(num="OptiArchitect - Non-Linear Programming")
    ax.plot(xs, ys, label="f(x)", color="blue")
    if x_star is not None and math.isfinite(x_star):
        ax.plot(x_star, obj.user_value(obj.f(x_star)), marker="o", ms=10, color="red",
                label=f"x* = {x_star:.4g}")

    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title(tx(title))
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200)
    if return_fig:
        return fig
    if show:
        plt.show()
    plt.close(fig)
