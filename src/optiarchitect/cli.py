#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiArchitect - interactive bilingual (English / Arabic) console program.

Usage
-----
    optiarchitect                  # interactive session   (same as: python -m optiarchitect)
    optiarchitect --lang ar        # start in Arabic
    optiarchitect --part 2         # jump straight to Part 2
    optiarchitect --selftest       # run the built-in verification suite
    optiarchitect --detail         # start with step-by-step tableaux/iterations ON
    optiarchitect --shape-ar       # reshape Arabic for consoles without bidi support
    optiarchitect --no-plot        # disable the graphical method

Browser version:  optiarchitect-web   (needs the "web" extra)
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import textwrap
from typing import List, Optional

import numpy as np

from optiarchitect.config import AUTHOR, COPYRIGHT, LICENSE, REPOSITORY, __version__
from optiarchitect.core import (choose_method, diagnose, grid_minimum, hungarian, run_method,
                                solve_lp, solve_transportation)
from optiarchitect.core.lp import format_tableau, lp_applicability
from optiarchitect.core.nlp import OptResult
from optiarchitect.examples import AS_EXAMPLES, LP_EXAMPLES, NL_EXAMPLES, TP_EXAMPLES
from optiarchitect.messages import TEXT
from optiarchitect.selftest import run_selftest
from optiarchitect.utils.parser import Objective, sp
from optiarchitect.utils.plot import plot_feasible_region
from optiarchitect.utils.text_fix import fix_ar


# ==========================================================================
#                         INTERACTIVE FRONT END (bilingual)
# ==========================================================================
class UI:
    """Console helper: language, shaping of Arabic, validated prompts, context help ('?')."""

    def __init__(self, lang: str = "en", shape: bool = False, detail: bool = False, plot: bool = True):
        self.shape, self.detail, self.plot = shape, detail, plot
        self.set_lang(lang)

    def set_lang(self, lang: str) -> None:
        self.lang, self.T = lang, TEXT[lang]

    # ---- output ---------------------------------------------------------
    def _shape(self, text: str) -> str:
        if self.lang == "ar" and self.shape:
            return "\n".join(fix_ar(line) for line in text.split("\n"))
        return text

    def s(self, key: str, **kw) -> str:
        text = self.T[key]
        return self._shape(text.format(**kw) if kw else text)

    def say(self, key: str, **kw) -> None:
        print(self.s(key, **kw))

    def wrapped(self, key: str, indent: str = "      ", width: int = 76) -> str:
        lines = textwrap.wrap(self.T[key], width=width - len(indent))
        return "\n".join(indent + self._shape(l) for l in lines)

    def pause(self, key: str = "c_press_enter") -> None:
        input(self.s(key))

    # ---- input ----------------------------------------------------------
    def _read(self, key: str, help_key: Optional[str] = None, **kw) -> str:
        while True:
            raw = input(self.s(key, **kw)).strip()
            if raw == "?":
                hk = "h_" + (help_key or key)
                print("   [?] " + self._shape(self.T.get(hk, self.T["h_generic"])))
                continue
            return raw

    def ask_text(self, key: str, default: str, **kw) -> str:
        return self._read(key, **kw) or default

    def ask_yes(self, key: str, default: bool = False, **kw) -> bool:
        raw = self._read(key, **kw).lower()
        if not raw:
            return default
        if raw in ("y", "yes", "1", "ن", "نعم"):
            return True
        if raw in ("n", "no", "0", "ل", "لا"):
            return False
        return default

    def ask_number(self, key, default, *, integer=False, minimum=None, maximum=None,
                   choices=None, help_key=None, **kw):
        while True:
            raw = self._read(key, help_key, **kw)
            if not raw:
                return default
            try:
                v = float(raw)
            except ValueError:
                self.say("c_err_number"); continue
            if not math.isfinite(v):
                self.say("c_err_number"); continue
            if (integer or choices is not None) and not v.is_integer():
                self.say("c_err_integer"); continue
            if choices is not None and v not in choices:
                self.say("c_err_choice", choices=list(choices)); continue
            if (minimum is not None and v < minimum) or (maximum is not None and v > maximum):
                self.say("c_err_range", lo=minimum if minimum is not None else "-inf",
                         hi=maximum if maximum is not None else "inf"); continue
            return int(v) if (integer or choices is not None) else v

    def ask_vector(self, key, k, *, nonneg=False, help_key=None, **kw):
        while True:
            raw = self._read(key, help_key, **kw).replace(",", " ").split()
            try:
                vals = [float(x) for x in raw]
            except ValueError:
                self.say("c_err_number"); continue
            if len(vals) != k:
                self.say("c_err_count", k=k); continue
            if not all(math.isfinite(x) for x in vals):
                self.say("c_err_number"); continue
            if nonneg and any(x < 0 for x in vals):
                self.say("c_err_nonneg"); continue
            return vals

    def ask_matrix(self, m, n, key="tp_cost_row", help_key=None):
        return np.array([self.ask_vector(key, n, help_key=help_key, i=i + 1) for i in range(m)])


def format_matrix(M, rows, cols, fmt="{:g}") -> str:
    body = [[fmt.format(x) for x in r] for r in M]
    w = max([len(c) for c in cols] + [len(x) for r in body for x in r] + [1])
    lw = max(len(r) for r in rows)
    lines = [" " * lw + "  " + "  ".join(c.rjust(w) for c in cols)]
    for lab, r in zip(rows, body):
        lines.append(lab.ljust(lw) + "  " + "  ".join(x.rjust(w) for x in r))
    return "\n".join("      " + ln for ln in lines)


def show_banner() -> None:
    print("=" * 71)
    print("   OPTIARCHITECT  v" + __version__ + "  |  OPERATIONS RESEARCH & OPTIMIZATION TOOLKIT")
    print("   Linear Programming - Transportation & Assignment - Non-Linear Optimization")
    print("   Developed by: " + AUTHOR)
    print("   Copyright " + COPYRIGHT + ". Released under the " + LICENSE + ".")
    print("=" * 71)


def _statement(ui: UI, key: str) -> None:
    print(ui.wrapped(key, "   ", 76))


def _observations(ui: UI, key: str) -> None:
    ui.say("c_ex_obs")
    print(ui.s(key))


# ==========================================================================
#                              PART 1 : UI
# ==========================================================================


def format_lp(c, A, b, types, obj) -> str:
    def expr(row):
        parts = [(("-" if v < 0 else "+"), (f"{abs(v):g}*" if abs(v) != 1 else "") + f"x{j + 1}")
                 for j, v in enumerate(row) if v != 0]
        if not parts:
            return "0"
        out = ("-" if parts[0][0] == "-" else "") + parts[0][1]
        return out + "".join(f" {sg} {t}" for sg, t in parts[1:])
    lines = [f"      {obj} Z = {expr(c)}", "      s.t."]
    lines += [f"         {expr(A[i])} {types[i]} {b[i]:g}" for i in range(len(b))]
    lines.append("         x >= 0")
    return "\n".join(lines)


def _print_trace(T, basis, names, title):
    print(f"\n   --- {title} ---")
    print(format_tableau(T, basis, names))


def _lp_collect(ui: UI, name: str):
    obj = "max" if ui.ask_number("lp_ask_obj", 1, integer=True, choices=[1, 2]) == 1 else "min"
    n = ui.ask_number("lp_ask_n", 2, integer=True, minimum=1, maximum=50)
    m = ui.ask_number("lp_ask_m", 2, integer=True, minimum=1, maximum=100)
    ui.say("lp_hdr_obj")
    c = np.array([ui.ask_number("lp_ask_c", 0, name=name, j=j + 1) for j in range(n)], dtype=float)
    ui.say("lp_hdr_con")
    A, b, types = np.zeros((m, n)), np.zeros(m), []
    for i in range(m):
        ui.say("lp_con_no", i=i + 1)
        for j in range(n):
            A[i, j] = ui.ask_number("lp_ask_a", 0, j=j + 1)
        types.append({1: "<=", 2: ">=", 3: "="}[ui.ask_number("lp_ask_rel", 1, integer=True, choices=[1, 2, 3])])
        b[i] = ui.ask_number("lp_ask_rhs", 0)
    return c, A, b, types, obj


def _lp_plot(ui: UI, c, A, b, types, obj, res, name) -> None:
    try:
        import matplotlib
    except ImportError:
        ui.say("lp_plot_missing")
        return
    headless = "agg" in matplotlib.get_backend().lower()
    path = "optiarchitect_lp_plot.png" if headless else None
    plot_feasible_region(c, A, b, types, obj, res, lang=ui.lang,
                         title=ui.T["lp_plot_title"].format(name=name),
                         show=not headless, save_path=path)
    if headless:
        ui.say("lp_plot_saved", path=path)


def run_lp(ui: UI, name: str, ex: Optional[int] = None) -> bool:
    ui.say("lp_title")
    if ex is None:
        c, A, b, types, obj = _lp_collect(ui, name)
    else:
        d = LP_EXAMPLES[ex]
        c, A, b = np.array(d["c"], float), np.array(d["A"], float), np.array(d["b"], float)
        types, obj = list(d["types"]), d["obj"]
        ui.say("c_ex_intro", title=ui.T[f"lp_ex{ex}_t"])
        _statement(ui, f"lp_ex{ex}_s")
    m, n = A.shape
    ui.say("lp_echo")
    print(format_lp(c, A, b, types, obj))

    c_eff = c if obj == "max" else -c
    rec = choose_method(c_eff, b, types)
    app = lp_applicability(c, b, types, obj)
    bar = "=" * 55
    print(f"\n{bar}\n   {ui.s('lp_rep_title')}\n{bar}")
    ui.say("lp_rep_welcome", name=name)
    ui.say("lp_rep_summary", n=n, m=m, obj=obj.upper())
    ui.say("lp_applic")
    for mth in ("standard", "dual", "two_phase"):
        ok, why = app[mth]
        print(f"   {ui.s('lp_ap_ok' if ok else 'lp_ap_no')} {ui.s('lp_m_' + mth)}: {ui.s(why)}")
    ui.say("lp_rec", method=ui.s("lp_m_" + rec))
    ui.say("lp_rep_reason", reason=ui.s(app[rec][1]))
    if rec == "two_phase":
        ui.say("lp_cmp_note")

    method = rec
    if ex is None:
        ch = ui.ask_number("lp_ask_method", 1, integer=True, choices=[1, 2, 3, 4])
        if ch > 1:
            want = {2: "standard", 3: "dual", 4: "two_phase"}[ch]
            if app[want][0]:
                method = want
            else:
                ui.say("lp_forced_bad", method=ui.s("lp_m_" + want), why=ui.s(app[want][1]))
        ui.pause("lp_press_enter")

    ui.say("lp_running", method=ui.s("lp_m_" + method))
    if ui.detail:
        ui.say("lp_trace_note")
    res = solve_lp(c, A, b, types, obj, method=method, trace=_print_trace if ui.detail else None)

    print(f"\n   ===== {ui.s('lp_sum_title', name=name)} =====")
    ui.say("lp_st_" + res.status)
    if res.status == "optimal":
        for j in range(n):
            print(f"   x{j + 1} = {res.x[j]:.6f}")
        ui.say("lp_obj_val", z=res.z)
        ui.say("lp_iters", k=res.iterations)
        ui.say("lp_viol", v=res.max_violation)
    print("   =====================================================")

    if n == 2:
        if ui.plot and ui.ask_yes("lp_ask_plot", True):
            _lp_plot(ui, c, A, b, types, obj, res, name)
    else:
        ui.say("lp_plot_skip")
    if ex is not None:
        _observations(ui, f"lp_ex{ex}_o")
    return (res.status == "optimal" and res.max_violation < 1e-7) or res.status in ("infeasible", "unbounded")


# ==========================================================================
#                              PART 2 : UI
# ==========================================================================


def run_transport(ui: UI, name: str, ex: Optional[int] = None) -> bool:
    ui.say("tp_title")
    if ex is None:
        ui.say("tp_hdr")
        m = ui.ask_number("tp_ask_m", 3, integer=True, minimum=1, maximum=30)
        n = ui.ask_number("tp_ask_n", 3, integer=True, minimum=1, maximum=30)
        ui.say("tp_cost_hdr", m=m, n=n)
        C = ui.ask_matrix(m, n)
        while True:
            S = np.array(ui.ask_vector("tp_ask_supply", m, nonneg=True, m=m))
            D = np.array(ui.ask_vector("tp_ask_demand", n, nonneg=True, n=n))
            if S.sum() > 0 and D.sum() > 0:
                break
            ui.say("c_err_total")
    else:
        d = TP_EXAMPLES[ex]
        C, S, D = np.array(d["C"], float), np.array(d["S"], float), np.array(d["D"], float)
        m, n = C.shape
        ui.say("c_ex_intro", title=ui.T[f"tp_ex{ex}_t"])
        _statement(ui, f"tp_ex{ex}_s")
    ui.say("c_data")
    print(format_matrix(C, [f"S{i + 1}" for i in range(m)], [f"D{j + 1}" for j in range(n)]))
    print(f"      Supply = {[float(x) for x in S]}  |  Demand = {[float(x) for x in D]}")

    res = solve_transportation(C, S, D)
    ts, td = float(S.sum()), float(D.sum())
    if res.dummy:
        ui.say("tp_bal_" + res.dummy, ts=ts, td=td, d=abs(ts - td))
    else:
        ui.say("tp_bal_ok", ts=ts)

    M, N = res.C.shape
    rl = [f"S{i + 1}" for i in range(M)]
    cl = [f"D{j + 1}" for j in range(N)]
    if res.dummy == "source":
        rl[-1] = "S*"
    if res.dummy == "destination":
        cl[-1] = "D*"

    print("\n" + "=" * 55 + "\n   " + ui.s("tp_rep", name=name) + "\n" + "=" * 55)
    ui.say("tp_sec_ibfs")
    for key in ("nw", "lc", "vam"):
        ui.say("tp_t_" + key)
        ui.say("tp_n_" + key)
        ib = res.ibfs[key]
        for k, st in enumerate(ib.steps, 1):
            i, j = st.cell[0] + 1, st.cell[1] + 1
            if key == "nw":
                msg = ui.s("tp_s_nw", q=st.qty, i=i, j=j)
            elif key == "lc":
                msg = ui.s("tp_s_lc", c=st.cost, q=st.qty, i=i, j=j)
            else:
                p = ui.s("tp_forced") if math.isinf(st.penalty) else f"{st.penalty:g}"
                msg = ui.s("tp_s_vam", p=p, c=st.cost, q=st.qty, i=i, j=j)
            print(f"       {k}. {msg}")
        ui.say("tp_alloc_hdr")
        print(format_matrix(ib.X, rl, cl))
        ui.say("tp_tot", m=key.upper(), c=ib.cost)

    sol = res.solution
    ui.say("tp_sec_opt")
    ui.say("tp_note_modi")
    ui.say("tp_start", m=res.start.upper(), c=res.ibfs[res.start].cost)
    if sol.zero_cells_added:
        ui.say("tp_degen", k=sol.zero_cells_added)
    for k, it in enumerate(sol.iterations, 1):
        ui.say("tp_it_line", k=k, i=it.entering[0] + 1, j=it.entering[1] + 1, d=it.delta, t=it.theta,
               a=it.leaving[0] + 1, b=it.leaving[1] + 1, c=it.cost_after)
        if ui.detail:
            ui.say("tp_loop", loop=" -> ".join(f"({a + 1},{b + 1})" for a, b in it.loop))
    ui.say("tp_uv", u=np.array2string(sol.u, precision=4), v=np.array2string(sol.v, precision=4))
    ui.say("tp_delta_hdr")
    print(format_matrix(sol.delta, rl, cl))
    if sol.status == "optimal":
        ui.say("tp_optimal", k=len(sol.iterations))
        if sol.alternative_optima:
            ui.say("tp_alt")
    else:
        ui.say("tp_limit")

    ui.say("tp_final_hdr")
    print(format_matrix(sol.X, rl, cl))
    ui.say("tp_final_cost", c=sol.cost)
    ui.say("tp_check", r=res.max_residual)
    if res.dummy == "source":
        for j in range(N):
            if sol.X[-1, j] > 1e-9:
                ui.say("tp_unmet", j=j + 1, q=sol.X[-1, j])
    elif res.dummy == "destination":
        for i in range(M):
            if sol.X[i, -1] > 1e-9:
                ui.say("tp_unused", i=i + 1, q=sol.X[i, -1])
    if ex is not None:
        _observations(ui, f"tp_ex{ex}_o")
    return sol.status == "optimal" and res.max_residual < 1e-7


def run_assignment(ui: UI, name: str, ex: Optional[int] = None) -> bool:
    ui.say("tp_title")
    if ex is None:
        ui.say("as_hdr")
        r = ui.ask_number("as_ask_rows", 3, integer=True, minimum=1, maximum=100)
        c = ui.ask_number("as_ask_cols", 3, integer=True, minimum=1, maximum=100)
        maximize = ui.ask_number("as_ask_max", 1, integer=True, choices=[1, 2]) == 2
        ui.say("tp_cost_hdr", m=r, n=c)
        C = ui.ask_matrix(r, c, help_key="as_row")
    else:
        d = AS_EXAMPLES[ex]
        C, maximize = np.array(d["C"], float), d["maximize"]
        r, c = C.shape
        ui.say("c_ex_intro", title=ui.T[f"tp_ex{ex}_t"])
        _statement(ui, f"tp_ex{ex}_s")
    ui.say("c_data")
    print(format_matrix(C, [f"R{i + 1}" for i in range(r)], [f"C{j + 1}" for j in range(c)]))

    print("\n" + "=" * 55 + "\n   " + ui.s("as_rep", name=name) + "\n" + "=" * 55)
    if r != c:
        ui.say("as_pad", r=r, c=c)
    res = hungarian(C, maximize=maximize)
    ui.say("as_h_title")
    ui.say("as_h_note")
    n = max(r, c)
    rl = [f"R{i + 1}" for i in range(n)]
    cl = [f"C{j + 1}" for j in range(n)]
    k = 0
    for st in res.steps:
        if st.kind == "row":
            ui.say("as_h_row")
        elif st.kind == "col":
            ui.say("as_h_col")
        elif st.kind == "adjust":
            k += 1
            ui.say("as_h_adj", k=k, a=st.matched, d=st.delta)
        else:
            ui.say("as_h_done", n=n)
            continue
        print(format_matrix(st.matrix, rl, cl))

    ui.say("as_res_hdr")
    for i, j in enumerate(res.assignment):
        if j is None:
            ui.say("as_res_dummy", i=i + 1)
        else:
            ui.say("as_res_row", i=i + 1, j=j + 1, c=C[i, j])
    for j in res.unassigned_cols:
        ui.say("as_res_free", j=j + 1)
    ui.say("as_tot_max" if maximize else "as_tot_min", c=res.cost)
    if ex is not None:
        _observations(ui, f"tp_ex{ex}_o")
    return True


# ==========================================================================
#                              PART 3 : UI
# ==========================================================================
METHOD_ORDER = ("golden", "fibonacci", "newton", "secant")


def _print_history(ui: UI, hist: List[dict], limit: int = 40):
    if not hist:
        return
    ui.say("nl_table")
    keys = list(hist[0].keys())
    print("      " + "  ".join(k.rjust(12) for k in keys))
    rows = hist if len(hist) <= limit else hist[:limit // 2] + hist[-limit // 2:]
    for h in rows:
        print("      " + "  ".join((str(h[k]) if k == "k" else f"{h[k]:.6g}").rjust(12) for k in keys))
    if len(hist) > limit:
        print(f"      ... ({len(hist) - limit} rows omitted)")


def run_nlp(ui: UI, name: str, ex: Optional[int] = None) -> bool:
    if sp is None:
        ui.say("c_no_sympy")
        return False
    ui.say("nl_title")
    if ex is None:
        while True:
            text = ui.ask_text("nl_ask_fun", ui.T["nl_default_fun"])
            try:
                Objective(text, 1)
                break
            except (ValueError, RuntimeError) as e:
                ui.say("nl_err_expr", e=e)
        sign = -1 if ui.ask_number("nl_ask_goal", 1, integer=True, choices=[1, 2]) == 2 else 1
        obj = Objective(text, sign)
        while True:
            a = ui.ask_number("nl_ask_a", 0.0)
            b = ui.ask_number("nl_ask_b", 5.0)
            if a < b:
                break
            ui.say("nl_err_interval")
        tol = ui.ask_number("nl_ask_tol", 1e-6, minimum=1e-12, maximum=1.0)
        while True:
            x0 = ui.ask_number("nl_ask_x0", (a + b) / 2)
            alt = x0 + 0.1 * (b - a)
            x1 = ui.ask_number("nl_ask_x1", alt if alt <= b else x0 - 0.1 * (b - a))
            if a <= x0 <= b and a <= x1 <= b and x0 != x1:
                break
            ui.say("nl_err_inside")
    else:
        d = NL_EXAMPLES[ex]
        obj = Objective(d["text"], d["sign"])
        a, b, tol, x0, x1 = d["a"], d["b"], d["tol"], d["x0"], d["x1"]
        ui.say("c_ex_intro", title=ui.T[f"nl_ex{ex}_t"])
        _statement(ui, f"nl_ex{ex}_s")

    print("\n" + "=" * 55 + f"\n   {ui.s('nl_rep', name=name)}\n" + "=" * 55)
    ui.say("nl_fun", t=obj.text)
    ui.say("nl_d1", t=obj.df_text)
    ui.say("nl_d2", t=obj.d2f_text)
    print(f"   [a, b] = [{a:g}, {b:g}] | tol = {tol:g} | x0 = {x0:g} | x1 = {x1:g}")
    if not obj.symbolic:
        ui.say("nl_numeric")

    ui.say("nl_sec_diag")
    diag = diagnose(obj, a, b, x0, x1)
    for m in METHOD_ORDER:
        okm, reason, params = diag[m]
        lab = "nl_bypassed" if not okm else ("nl_caution" if reason == "uni_multimodal" else "nl_applicable")
        print(f"   {ui.s(lab)} {ui.s('nl_m_' + m)}: {ui.s(reason, **params)}")

    ui.say("nl_sec_res")
    results: List[OptResult] = []
    for m in METHOD_ORDER:
        if not diag[m][0]:
            continue
        r = run_method(obj, m, a, b, x0, x1, tol)
        results.append(r)
        print("\n   " + ui.s("nl_res", m=ui.s("nl_m_" + m), x=r.x, fx=obj.user_value(r.fx), it=r.iterations, ev=r.evals))
        ui.say("nl_status", s=ui.s("st_" + r.status))
        for code, params in r.notes:
            ui.say("n_" + code, **params)
        if ui.detail:
            _print_history(ui, r.history)

    ui.say("nl_sec_ver")
    gx, gf = grid_minimum(obj.f, a, b)
    ui.say("nl_grid", x=gx, fx=obj.user_value(gf))
    good = [r for r in results if r.status == "converged"]
    if not good:
        ui.say("nl_none")
        return False
    best = min(good, key=lambda r: r.fx)
    ui.say("nl_best", m=ui.s("nl_m_" + best.method), x=best.x, fx=obj.user_value(best.fx))
    verified = best.fx <= gf + 1e-6 * (1.0 + abs(gf))
    ui.say("nl_agree" if verified else "nl_worse")
    if ex is not None:
        _observations(ui, f"nl_ex{ex}_o")
    return verified


# ==========================================================================
#                         MENUS, SELF-TEST, ENTRY POINT
# ==========================================================================
_PART_RUN = {1: ("lp_name", "lp_ex_menu", (1, 2, 3)), 2: ("tp_name", "tp_ex_menu", (1, 2, 3, 4)),
             3: ("nl_name", "nl_ex_menu", (1, 2, 3))}


def print_main_menu(ui: UI) -> None:
    print("\n" + "=" * 71 + "\n   " + ui.s("c_menu_title") + "\n" + "=" * 71)
    for p in (1, 2, 3):
        print(ui.s(f"c_p{p}_title"))
        print(ui.wrapped(f"c_p{p}_sum", "      ", 76))
    print()
    ui.say("c_m_guide")
    ui.say("c_m_detail", state=ui.s("c_on" if ui.detail else "c_off"))
    for k in ("c_m_lang", "c_m_test", "c_m_about", "c_m_exit"):
        ui.say(k)


def _run_safely(ui: UI, fn, *args) -> bool:
    try:
        return bool(fn(*args))
    except (ValueError, RuntimeError, ArithmeticError, np.linalg.LinAlgError) as e:
        ui.say("c_error", e=e)
        return False


def part_menu(ui: UI, name: str, part: int) -> None:
    title_key, ex_menu_key, ex_range = _PART_RUN[part]
    while True:
        short = ui.T[f"c_p{part}_title"].split("] ", 1)[-1]
        print("\n" + "-" * 71)
        print(ui._shape(ui.T["c_sub_title"].format(part=short)))
        for k in ("c_sub_own", "c_sub_ex", "c_sub_learn", "c_sub_back"):
            ui.say(k)
        ch = ui.ask_number("c_ask_sub", 1, integer=True, choices=[0, 1, 2, 3])
        if ch == 0:
            return
        if ch == 3:
            print(ui.s(f"{('lp', 'tp', 'nl')[part - 1]}_learn"))
            ui.pause()
            continue
        if ch == 1:
            if part == 1:
                fn, args = run_lp, ()
            elif part == 3:
                fn, args = run_nlp, ()
            else:
                kind = ui.ask_number("tp_ask_kind", 1, integer=True, choices=[1, 2])
                fn, args = (run_assignment if kind == 2 else run_transport), ()
        else:
            print(ui.s(ex_menu_key))
            pick = ui.ask_number("c_ex_pick", 1, integer=True, choices=list(ex_range))
            fn = {1: run_lp, 3: run_nlp}.get(part) or (run_assignment if pick >= 3 else run_transport)
            args = (pick,)
        ok = _run_safely(ui, fn, ui, name, *args)
        print(ui.s("c_ft", part=ui.T[title_key], status=ui.s("c_ft_ok" if ok else "c_ft_fail")))
        ui.say("c_again_hint")


# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def selftest(ui: Optional[UI] = None) -> bool:
    """Reproduce reference results, cross-validate solvers against each other, check i18n tables."""
    ui = ui or UI("en")
    ui.say("c_st_hdr")
    passed = total = 0
    for label, r in run_selftest():
        tag = ui.s("c_st_skip") if r is None else ui.s("c_st_pass") if r else ui.s("c_st_fail")
        print(f"   [{tag}] {label}")
        if r is not None:
            total += 1
            passed += bool(r)
    ui.say("c_st_sum", p=passed, t=total)
    return passed == total


def choose_language() -> str:
    print("Select interface language / اختر لغة الواجهة:\n  1. English\n  2. العربية\n")
    while True:
        ch = input("Enter choice (1 or 2) [Default: 1] / أدخل خيارك: ").strip() or "1"
        if ch in ("1", "2"):
            return "en" if ch == "1" else "ar"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="OptiArchitect - bilingual OR & optimization teaching toolkit")
    ap.add_argument("--lang", choices=["en", "ar"], help="interface language (default: ask)")
    ap.add_argument("--part", type=int, choices=[1, 2, 3], help="open this part directly")
    ap.add_argument("--no-plot", action="store_true", help="disable the graphical method")
    ap.add_argument("--detail", action="store_true", help="start with step-by-step detail mode ON")
    ap.add_argument("--shape-ar", action="store_true", help="reshape Arabic text for consoles without bidi support")
    ap.add_argument("--selftest", action="store_true", help="run the built-in verification suite and exit")
    ap.add_argument("--version", action="version", version=f"OptiArchitect {__version__} - {COPYRIGHT} - {LICENSE}")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    shape = args.shape_ar or os.environ.get("OPTI_AR_SHAPE") == "1"
    if args.selftest:
        return 0 if selftest(UI(args.lang or "en", shape)) else 1

    show_banner()
    ui = UI("en", shape, args.detail, not args.no_plot)
    try:
        ui.set_lang(args.lang or choose_language())
        if ui.lang == "ar" and not shape:
            ui.say("c_shape_hint")
        name = ui.ask_text("c_ask_name", ui.T["c_default_name"])
        ui.say("c_welcome", name=name)
        pending = args.part
        while True:
            if pending:
                part_menu(ui, name, pending)
                pending = None
            print_main_menu(ui)
            ch = ui.ask_number("c_ask_menu", 1, integer=True, choices=list(range(9)))
            if ch == 0:
                break
            if ch in (1, 2, 3):
                part_menu(ui, name, ch)
            elif ch == 4:
                print(ui.s("c_guide")); ui.pause()
            elif ch == 5:
                ui.detail = not ui.detail
                ui.say("c_detail_now", state=ui.s("c_on" if ui.detail else "c_off"))
            elif ch == 6:
                ui.set_lang("ar" if ui.lang == "en" else "en")
            elif ch == 7:
                selftest(ui); ui.pause()
            elif ch == 8:
                print(ui.s("c_about", ver=__version__, author=AUTHOR, copyright=COPYRIGHT, license=LICENSE, url=REPOSITORY)); ui.pause()
        ui.say("c_bye")
    except (KeyboardInterrupt, EOFError):
        print(ui.s("c_aborted"))
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
