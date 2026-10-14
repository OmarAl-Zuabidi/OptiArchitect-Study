#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiArchitect - web front end (Streamlit)
=========================================
A browser version of the interactive, bilingual (English / Arabic) console program
``group.py``.  It is a *front end only*: every number comes from the same pure solver
cores (core/, utils/) and every sentence comes from the same message table
(messages.py), so the web and console versions behave identically.

Mapping console menu -> web
---------------------------
    [1] Part 1  Linear Programming ........ sidebar page  "Part 1"
    [2] Part 2  Transportation/Assignment . sidebar page  "Part 2"
    [3] Part 3  Non-linear optimization ... sidebar page  "Part 3"
    [4] User guide ........................ sidebar page  "User guide"
    [5] Step-by-step detail mode .......... sidebar checkbox
    [6] Language (EN / AR) ................ sidebar selector
    [7] Built-in self-test ................ sidebar page  "Self-test"
    [8] About / author / licence .......... sidebar page  "About"
    --no-plot ............................. sidebar checkbox
    "?" help at a prompt .................. the (?) tooltip / caption next to each field

Inside each part: solve your own problem / worked example / read about the methods.

Run
---
    pip install "optiarchitect[web]"     # or, from a clone:  pip install -e ".[web]"
    optiarchitect-web                    # launcher for:  streamlit run optiarchitect/app.py

Deep links:  ?lang=ar&page=part2
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import html
import json
import math
import re
import textwrap
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import streamlit as st

try:                                           # headless backend: figures go to the browser
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:                            # pragma: no cover
    matplotlib = None
    plt = None

from optiarchitect.config import AUTHOR, COPYRIGHT, LICENSE, REPOSITORY, VALID_TYPES, __version__
from optiarchitect.core import (choose_method, diagnose, grid_minimum, hungarian, run_method,
                  solve_lp, solve_transportation)
from optiarchitect.core.lp import lp_applicability
from optiarchitect.examples import AS_EXAMPLES, EXAMPLE_RANGE, LP_EXAMPLES, NL_EXAMPLES, TP_EXAMPLES
from optiarchitect.messages import TEXT
from optiarchitect.selftest import run_selftest
from optiarchitect.utils.parser import Objective, sp
from optiarchitect.utils.plot import plot_feasible_region, plot_nlp_1d

PAGE_CONFIG = dict(page_title="OptiArchitect - Operations Research", page_icon="📈", layout="wide")


# --------------------------------------------------------------------------
# Optional research-study hooks (see optiarchitect.study). They do nothing unless the study
# application switched them on (session flag "study_active"), so the normal web application
# behaves exactly as before.
# --------------------------------------------------------------------------
def _jsonable(x):
    """Convert numpy / non-finite values to plain JSON-safe Python objects."""
    if isinstance(x, np.ndarray):
        return _jsonable(x.tolist())
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        x = float(x)
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [_jsonable(v) for v in x]
    if x is None or isinstance(x, (str, int, bool)):
        return x
    return str(x)


def record_problem(kind: str, scope: str, example, data: dict, result: dict) -> None:
    """Remember one problem the participant ran (study mode only; idempotent across Streamlit reruns)."""
    if not st.session_state.get("study_active"):
        return
    payload = _jsonable(dict(kind=kind, scope=scope, example=example, input=data))
    key = hashlib.sha1(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    log = st.session_state.setdefault("study_problems", {})
    if key not in log:
        log[key] = dict(payload, first_seen=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
                        result=_jsonable(result))


def record_page(page: str) -> None:
    """Remember which pages the participant visited (study mode only)."""
    if st.session_state.get("study_active"):
        pages = st.session_state.setdefault("study_pages", [])
        if page not in pages:
            pages.append(page)


def record_flag(name: str) -> None:
    """Remember that a feature was used at least once (study mode only)."""
    if st.session_state.get("study_active"):
        st.session_state.setdefault("study_flags", {})[name] = True


# --------------------------------------------------------------------------
# Web-only captions (widgets that do not exist in a console).  Everything that
# the console prints or asks comes from messages.TEXT.
# --------------------------------------------------------------------------
WEB: Dict[str, Dict[str, str]] = {
    "en": dict(
        home="Home", nav="Navigation", lang="Language / لغة العرض",
        detail="Step-by-step detail mode (tableaux / loops / iteration tables)",
        plot="Enable the graphical method", solve="Solve", run_ex="Run the worked example",
        example="Worked example", mx="Maximize", mn="Minimize", auto="Automatic (recommended)",
        transport="Transportation problem", assign="Assignment problem", kind="Problem type",
        obj_lp="Objective type", obj_as="Objective", cost="Minimize cost", profit="Maximize profit",
        goal="Goal", method="Method", rel="Relation", rhs="RHS",
        download="Download CSV", curve="Plot of f(x) and the best result",
        spin="Running the verification suite...", run_test="Run the self-test", value="Value",
        variable="Variable", tabs="Simplex tableaux", omitted="... ({k} tableaux omitted)",
        omitted_rows="... ({k} rows omitted)", hist="Iteration table",
        tol_hint="Scientific notation is accepted, e.g. 1e-6",
        banner2="Linear Programming - Transportation & Assignment - Non-Linear Optimization",
        dev="Developed by", web_tip="Hover over the (?) icons or read the grey captions for field help.",
        supply="Supply", demand="Demand",
    ),
    "ar": dict(
        home="الرئيسية", nav="التنقل", lang="Language / لغة العرض",
        detail="وضع الشرح خطوة بخطوة (الجداول / الحلقات / جداول التكرار)",
        plot="تفعيل الطريقة البيانية", solve="حل المسألة", run_ex="تشغيل المثال المحلول",
        example="المثال المحلول", mx="تعظيم", mn="تصغير", auto="تلقائي (موصى به)",
        transport="مسألة النقل", assign="مسألة التخصيص", kind="نوع المسألة",
        obj_lp="نوع دالة الهدف", obj_as="الهدف", cost="تصغير التكلفة", profit="تعظيم الربح",
        goal="الهدف", method="الطريقة", rel="العلاقة", rhs="الطرف الأيمن",
        download="تحميل CSV", curve="رسم الدالة f(x) وأفضل نتيجة",
        spin="جارٍ تشغيل اختبارات التحقق...", run_test="تشغيل الاختبار الذاتي", value="القيمة",
        variable="المتغير", tabs="جداول السمبلكس", omitted="... (تم إخفاء {k} جدول)",
        omitted_rows="... (تم إخفاء {k} صف)", hist="جدول التكرارات",
        tol_hint="يمكن استخدام الصيغة العلمية، مثل 1e-6",
        banner2="البرمجة الخطية - النقل والتخصيص - التحسين غير الخطي",
        dev="تطوير", web_tip="مرّر المؤشر فوق أيقونات (?) أو اقرأ الشروحات الرمادية للمساعدة في كل حقل.",
        supply="العرض", demand="الطلب",
    ),
}

CSS = """
<style>
.oa-msg{white-space:pre-wrap;margin:.12rem 0;line-height:1.55;font-size:.95rem;unicode-bidi:plaintext}
.oa-mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.88rem}
.oa-ok,.oa-warn,.oa-err,.oa-info{padding:.25rem .6rem;border-radius:4px;border-inline-start:4px solid}
.oa-ok{border-color:#2e7d32;background:rgba(46,125,50,.10)}
.oa-warn{border-color:#ef6c00;background:rgba(239,108,0,.10)}
.oa-err{border-color:#c62828;background:rgba(198,40,40,.10)}
.oa-info{border-color:#1565c0;background:rgba(21,101,192,.10)}
.oa-h{font-weight:700;font-size:1.08rem;margin:1rem 0 .35rem;padding-bottom:.15rem;
      border-bottom:1px solid rgba(128,128,128,.35);unicode-bidi:plaintext}
.oa-title{font-weight:800;font-size:1.55rem;letter-spacing:.02em;margin-bottom:.1rem}
.oa-sub{opacity:.8;font-size:.92rem;margin:.05rem 0}
</style>
"""
CSS_RTL = """
<style>
.block-container,[data-testid="stSidebar"] *{direction:rtl;text-align:right}
[data-testid="stDataFrame"],[data-testid="stTable"],[data-testid="stImage"],pre,code,
[data-testid="stDataEditor"]{direction:ltr;text-align:left}
</style>
"""

_TAGS = (("[X]", "err"), ("[!]", "warn"), ("[V]", "ok"), ("[i]", "info"),
         ("[BYPASSED]", "warn"), ("[CAUTION]", "warn"), ("[APPLICABLE]", "ok"))
_RULE = re.compile(r"^\s*[=\-]{10,}\s*$")
_PREFIX = re.compile(r"^\s*\[\d\]\s*")


# ==========================================================================
#                            TEXT / LAYOUT HELPERS
# ==========================================================================
class UI:
    """Web counterpart of the console ``UI`` class: language, text lookup, rendering."""

    def __init__(self, lang: str, detail: bool, plot: bool):
        self.lang, self.detail, self.plot = lang, detail, plot
        self.T = TEXT[lang]
        self.W = WEB[lang]

    # ---- text ---------------------------------------------------------
    def s(self, key: str, **kw) -> str:
        text = self.T[key]
        return text.format(**kw) if kw else text

    def label(self, key: str, **kw) -> str:
        """Console prompt -> widget label (drops the trailing colon / '(Y/n)')."""
        t = self.s(key, **kw).strip().rstrip(":").strip()
        return re.sub(r"\s*\(Y/n\)$", "", t)

    def tip(self, key: str) -> Optional[str]:
        return self.T.get("h_" + key)

    def short(self, text: str) -> str:
        return _PREFIX.sub("", text).strip()

    def title_of(self, key: str) -> str:
        return self.short(self.s(key)).rstrip(":").strip()

    # ---- rendering ----------------------------------------------------
    def raw(self, text: str, kind: Optional[str] = None, mono: bool = False) -> None:
        lines = [ln.rstrip() for ln in text.split("\n") if not _RULE.match(ln)]
        body = textwrap.dedent("\n".join(lines)).strip("\n")
        if not body.strip():
            return
        if kind is None:
            head = body.lstrip()
            kind = next((k for tag, k in _TAGS if head.startswith(tag)), None)
        cls = "oa-msg" + (f" oa-{kind}" if kind else "") + (" oa-mono" if mono else "")
        st.markdown(f'<div class="{cls}" dir="auto">{html.escape(body)}</div>', unsafe_allow_html=True)

    def say(self, key: str, kind: Optional[str] = None, mono: bool = False, **kw) -> None:
        self.raw(self.s(key, **kw), kind, mono)

    def heading(self, text: str) -> None:
        clean = text.strip("\n -=").strip()
        st.markdown(f'<div class="oa-h" dir="auto">{html.escape(clean)}</div>', unsafe_allow_html=True)

    def head(self, key: str, **kw) -> None:
        self.heading(self.s(key, **kw))

    def hint(self, key: str) -> None:
        """Console '?' help for widgets that cannot show a tooltip (tables)."""
        t = self.tip(key)
        if t:
            st.caption(t)

    def table(self, df: pd.DataFrame) -> None:
        st.table(df)

    def download(self, df: pd.DataFrame, fname: str, scope: str) -> None:
        st.download_button(self.W["download"], df.to_csv().encode("utf-8-sig"), file_name=fname,
                           mime="text/csv", key=f"dl_{scope}_{fname}")


def mdf(M, rows, cols, fmt="{:g}") -> pd.DataFrame:
    """Matrix -> table, formatted like the console ``format_matrix``."""
    return pd.DataFrame([[fmt.format(x) for x in r] for r in M], index=list(rows), columns=list(cols))


def numeric_grid(ui: UI, df: pd.DataFrame, *, nonneg: bool = False) -> Optional[np.ndarray]:
    """Validate an edited grid like the console ``ask_vector`` (finite numbers, optional >= 0)."""
    try:
        arr = df.to_numpy(dtype=float)
    except (TypeError, ValueError):
        ui.say("c_err_number")
        return None
    if not np.isfinite(arr).all():
        ui.say("c_err_number")
        return None
    if nonneg and (arr < 0).any():
        ui.say("c_err_nonneg")
        return None
    return arr


# ==========================================================================
#                                 PART 1: LP
# ==========================================================================
def format_lp(c, A, b, types, obj) -> str:
    def expr(row):
        parts = [(("-" if v < 0 else "+"), (f"{abs(v):g}*" if abs(v) != 1 else "") + f"x{j + 1}")
                 for j, v in enumerate(row) if v != 0]
        if not parts:
            return "0"
        out = ("-" if parts[0][0] == "-" else "") + parts[0][1]
        return out + "".join(f" {sg} {t}" for sg, t in parts[1:])
    lines = [f"{obj} Z = {expr(c)}", "s.t."]
    lines += [f"   {expr(A[i])} {types[i]} {b[i]:g}" for i in range(len(b))]
    lines.append("   x >= 0")
    return "\n".join(lines)


def _tableau_df(T, basis, names) -> pd.DataFrame:
    cols = list(names[:T.shape[1] - 1]) + ["RHS"]
    idx = [names[b] for b in basis] + ["Z"]
    return pd.DataFrame([[f"{v:.4g}" for v in row] for row in T], index=idx, columns=cols)


def lp_inputs(ui: UI) -> Optional[dict]:
    W = ui.W
    obj = st.radio(W["obj_lp"], ["max", "min"], horizontal=True, key="lp_obj", help=ui.tip("lp_ask_obj"),
                   format_func=lambda k: ("MAX - " + W["mx"]) if k == "max" else ("MIN - " + W["mn"]))
    c1, c2 = st.columns(2)
    n = int(c1.number_input(ui.label("lp_ask_n"), 1, 50, 2, 1, key="lp_n", help=ui.tip("lp_ask_n")))
    m = int(c2.number_input(ui.label("lp_ask_m"), 1, 100, 2, 1, key="lp_m", help=ui.tip("lp_ask_m")))
    xs = [f"x{j + 1}" for j in range(n)]

    ui.head("lp_hdr_obj")
    ui.hint("lp_ask_c")
    c_df = st.data_editor(pd.DataFrame([[0.0] * n], columns=xs, index=["Z"]), key=f"lp_c_{n}")

    ui.head("lp_hdr_con")
    ui.hint("lp_ask_rel")
    base = pd.DataFrame(0.0, index=[f"C{i + 1}" for i in range(m)], columns=xs)
    base["rel"] = "<="                      # fixed internal names: edits survive a language switch
    base["rhs"] = 0.0
    cfg = {"rel": st.column_config.SelectboxColumn(W["rel"], options=list(VALID_TYPES), required=True),
           "rhs": st.column_config.NumberColumn(W["rhs"])}
    k_df = st.data_editor(base, column_config=cfg, key=f"lp_k_{n}_{m}")

    method = st.radio(W["method"], ["auto", "standard", "dual", "two_phase"], horizontal=True, key="lp_method",
                      help=ui.tip("lp_ask_method"),
                      format_func=lambda k: W["auto"] if k == "auto" else ui.s("lp_m_" + k))
    if not st.button(W["solve"], type="primary", key="lp_go"):
        return None
    c = numeric_grid(ui, c_df)
    A = numeric_grid(ui, k_df[xs])
    b = numeric_grid(ui, k_df[["rhs"]])
    types = [str(t) for t in k_df["rel"]]
    if c is None or A is None or b is None:
        return None
    if any(t not in VALID_TYPES for t in types):
        ui.say("c_err_choice", choices=list(VALID_TYPES))
        return None
    return dict(c=c[0].tolist(), A=A.tolist(), b=b[:, 0].tolist(), types=types, obj=obj, method=method)


def render_lp(ui: UI, name: str, d: dict, ex: Optional[int], scope: str) -> bool:
    ui.head("lp_title")
    c, A, b = np.array(d["c"], float), np.array(d["A"], float), np.array(d["b"], float)
    types, obj = list(d["types"]), d["obj"]
    if ex is not None:
        ui.say("c_ex_intro", title=ui.T[f"lp_ex{ex}_t"])
        ui.say(f"lp_ex{ex}_s")
    m, n = A.shape
    ui.say("lp_echo")
    st.code(format_lp(c, A, b, types, obj), language="text")

    c_eff = c if obj == "max" else -c
    rec = choose_method(c_eff, b, types)
    app = lp_applicability(c, b, types, obj)
    ui.head("lp_rep_title")
    ui.say("lp_rep_welcome", name=name)
    ui.say("lp_rep_summary", n=n, m=m, obj=obj.upper())
    ui.say("lp_applic")
    for mth in ("standard", "dual", "two_phase"):
        ok, why = app[mth]
        ui.raw(f"{ui.s('lp_ap_ok' if ok else 'lp_ap_no')} {ui.s('lp_m_' + mth)}: {ui.s(why)}")
    ui.say("lp_rec", method=ui.s("lp_m_" + rec))
    ui.say("lp_rep_reason", reason=ui.s(app[rec][1]))
    if rec == "two_phase":
        ui.say("lp_cmp_note")

    method, want = rec, d.get("method", "auto")
    if want != "auto":
        if app[want][0]:
            method = want
        else:
            ui.say("lp_forced_bad", method=ui.s("lp_m_" + want), why=ui.s(app[want][1]))

    ui.say("lp_running", method=ui.s("lp_m_" + method))
    traces: List[Optional[tuple]] = []

    def tracer(T, basis, names_, title):
        traces.append((title, _tableau_df(T, basis, names_)) if len(traces) < 400 else None)

    res = solve_lp(c, A, b, types, obj, method=method, trace=tracer if ui.detail else None)
    record_problem("lp", scope, ex, d, dict(
        method=res.method, requested_method=d.get("method", "auto"), status=res.status, objective_value=res.z,
        solution=res.x, iterations=res.iterations, max_violation=res.max_violation,
        n_variables=n, n_constraints=m, sense=obj))

    if ui.detail:
        ui.say("lp_trace_note")
        shown = [t for t in traces if t is not None]
        with st.expander(f"{ui.W['tabs']} ({len(traces)})", expanded=False):
            for title, df in shown:
                st.markdown(f"**{title}**")
                ui.table(df)
            if len(shown) < len(traces):
                st.caption(ui.W["omitted"].format(k=len(traces) - len(shown)))

    ui.head("lp_sum_title", name=name)
    kind = {"optimal": "ok", "infeasible": "warn", "unbounded": "warn"}.get(res.status, "err")
    ui.say("lp_st_" + res.status, kind=kind)
    if res.status == "optimal":
        sol = pd.DataFrame({ui.W["variable"]: [f"x{j + 1}" for j in range(n)],
                            ui.W["value"]: [f"{res.x[j]:.6f}" for j in range(n)]}).set_index(ui.W["variable"])
        ui.table(sol)
        ui.say("lp_obj_val", z=res.z)
        ui.say("lp_iters", k=res.iterations)
        ui.say("lp_viol", v=res.max_violation)
        ui.download(sol, "lp_solution.csv", scope)

    if n == 2:
        if ui.plot and st.checkbox(ui.label("lp_ask_plot"), value=True, key=f"lp_plot_{scope}"):
            if plt is None:
                ui.say("lp_plot_missing")
            else:
                fig = plot_feasible_region(c, A, b, types, obj, res, lang=ui.lang,
                                           title=ui.T["lp_plot_title"].format(name=name),
                                           show=False, return_fig=True)
                st.pyplot(fig)
                plt.close(fig)
    else:
        ui.say("lp_plot_skip")
    if ex is not None:
        ui.say("c_ex_obs")
        ui.say(f"lp_ex{ex}_o")
    return (res.status == "optimal" and res.max_violation < 1e-7) or res.status in ("infeasible", "unbounded")


# ==========================================================================
#                      PART 2: TRANSPORTATION & ASSIGNMENT
# ==========================================================================
def tp_inputs(ui: UI) -> Optional[dict]:
    W = ui.W
    ui.say("tp_hdr")
    c1, c2 = st.columns(2)
    m = int(c1.number_input(ui.label("tp_ask_m"), 1, 30, 3, 1, key="tp_m", help=ui.tip("tp_ask_m")))
    n = int(c2.number_input(ui.label("tp_ask_n"), 1, 30, 3, 1, key="tp_n", help=ui.tip("tp_ask_n")))
    rows, cols = [f"S{i + 1}" for i in range(m)], [f"D{j + 1}" for j in range(n)]
    ui.say("tp_cost_hdr", m=m, n=n)
    ui.hint("tp_cost_row")
    C_df = st.data_editor(pd.DataFrame(0.0, index=rows, columns=cols), key=f"tp_c_{m}_{n}")
    ui.say("tp_ask_supply", m=m)
    ui.hint("tp_ask_supply")
    S_df = st.data_editor(pd.DataFrame([[0.0] * m], index=["S"], columns=rows), key=f"tp_s_{m}")
    ui.say("tp_ask_demand", n=n)
    ui.hint("tp_ask_demand")
    D_df = st.data_editor(pd.DataFrame([[0.0] * n], index=["D"], columns=cols), key=f"tp_d_{n}")
    if not st.button(W["solve"], type="primary", key="tp_go"):
        return None
    C, S, D = numeric_grid(ui, C_df), numeric_grid(ui, S_df, nonneg=True), numeric_grid(ui, D_df, nonneg=True)
    if C is None or S is None or D is None:
        return None
    if S.sum() <= 0 or D.sum() <= 0:
        ui.say("c_err_total")
        return None
    return dict(C=C.tolist(), S=S[0].tolist(), D=D[0].tolist())


def as_inputs(ui: UI) -> Optional[dict]:
    W = ui.W
    ui.say("as_hdr")
    c1, c2 = st.columns(2)
    r = int(c1.number_input(ui.label("as_ask_rows"), 1, 100, 3, 1, key="as_r", help=ui.tip("as_ask_rows")))
    c = int(c2.number_input(ui.label("as_ask_cols"), 1, 100, 3, 1, key="as_c", help=ui.tip("as_ask_cols")))
    maximize = st.radio(W["obj_as"], [False, True], horizontal=True, key="as_max", help=ui.tip("as_ask_max"),
                        format_func=lambda v: W["profit"] if v else W["cost"])
    ui.say("tp_cost_hdr", m=r, n=c)
    ui.hint("as_row")
    C_df = st.data_editor(pd.DataFrame(0.0, index=[f"R{i + 1}" for i in range(r)],
                                       columns=[f"C{j + 1}" for j in range(c)]), key=f"as_m_{r}_{c}")
    if not st.button(W["solve"], type="primary", key="as_go"):
        return None
    C = numeric_grid(ui, C_df)
    return None if C is None else dict(C=C.tolist(), maximize=bool(maximize))


def render_transport(ui: UI, name: str, d: dict, ex: Optional[int], scope: str) -> bool:
    ui.head("tp_title")
    C, S, D = np.array(d["C"], float), np.array(d["S"], float), np.array(d["D"], float)
    m, n = C.shape
    if ex is not None:
        ui.say("c_ex_intro", title=ui.T[f"tp_ex{ex}_t"])
        ui.say(f"tp_ex{ex}_s")
    ui.say("c_data")
    ui.table(mdf(C, [f"S{i + 1}" for i in range(m)], [f"D{j + 1}" for j in range(n)]))
    ui.raw(f"Supply = {[float(x) for x in S]}  |  Demand = {[float(x) for x in D]}", mono=True)

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

    ui.head("tp_rep", name=name)
    ui.head("tp_sec_ibfs")
    for key in ("nw", "lc", "vam"):
        ib = res.ibfs[key]
        with st.expander(ui.title_of("tp_t_" + key), expanded=(key == res.start)):
            ui.say("tp_n_" + key)
            lines = []
            for k, stp in enumerate(ib.steps, 1):
                i, j = stp.cell[0] + 1, stp.cell[1] + 1
                if key == "nw":
                    msg = ui.s("tp_s_nw", q=stp.qty, i=i, j=j)
                elif key == "lc":
                    msg = ui.s("tp_s_lc", c=stp.cost, q=stp.qty, i=i, j=j)
                else:
                    p = ui.s("tp_forced") if math.isinf(stp.penalty) else f"{stp.penalty:g}"
                    msg = ui.s("tp_s_vam", p=p, c=stp.cost, q=stp.qty, i=i, j=j)
                lines.append(f"{k}. {msg}")
            ui.raw("\n".join(lines))
            ui.say("tp_alloc_hdr")
            ui.table(mdf(ib.X, rl, cl))
            ui.say("tp_tot", m=key.upper(), c=ib.cost)

    sol = res.solution
    record_problem("transportation", scope, ex, d, dict(
        dummy=res.dummy, start=res.start, initial_costs={k: v.cost for k, v in res.ibfs.items()},
        optimal_cost=sol.cost, status=sol.status, modi_iterations=len(sol.iterations),
        degeneracy_repairs=sol.zero_cells_added, alternative_optima=sol.alternative_optima,
        max_residual=res.max_residual, plan=sol.X, sources=m, destinations=n))
    ui.head("tp_sec_opt")
    ui.say("tp_note_modi")
    ui.say("tp_start", m=res.start.upper(), c=res.ibfs[res.start].cost)
    if sol.zero_cells_added:
        ui.say("tp_degen", k=sol.zero_cells_added)
    lines = []
    for k, it in enumerate(sol.iterations, 1):
        lines.append(ui.s("tp_it_line", k=k, i=it.entering[0] + 1, j=it.entering[1] + 1, d=it.delta, t=it.theta,
                          a=it.leaving[0] + 1, b=it.leaving[1] + 1, c=it.cost_after))
        if ui.detail:
            lines.append(ui.s("tp_loop", loop=" -> ".join(f"({a + 1},{b + 1})" for a, b in it.loop)))
    if lines:
        ui.raw("\n".join(lines))
    ui.say("tp_uv", u=np.array2string(sol.u, precision=4), v=np.array2string(sol.v, precision=4))
    ui.say("tp_delta_hdr")
    ui.table(mdf(sol.delta, rl, cl))
    if sol.status == "optimal":
        ui.say("tp_optimal", k=len(sol.iterations))
        if sol.alternative_optima:
            ui.say("tp_alt")
    else:
        ui.say("tp_limit")

    ui.head("tp_final_hdr")
    final = mdf(sol.X, rl, cl)
    ui.table(final)
    ui.say("tp_final_cost", c=sol.cost, kind="ok")
    ui.say("tp_check", r=res.max_residual)
    if res.dummy == "source":
        for j in range(N):
            if sol.X[-1, j] > 1e-9:
                ui.say("tp_unmet", j=j + 1, q=sol.X[-1, j])
    elif res.dummy == "destination":
        for i in range(M):
            if sol.X[i, -1] > 1e-9:
                ui.say("tp_unused", i=i + 1, q=sol.X[i, -1])
    ui.download(final, "transport_plan.csv", scope)
    if ex is not None:
        ui.say("c_ex_obs")
        ui.say(f"tp_ex{ex}_o")
    return sol.status == "optimal" and res.max_residual < 1e-7


def render_assignment(ui: UI, name: str, d: dict, ex: Optional[int], scope: str) -> bool:
    ui.head("tp_title")
    C, maximize = np.array(d["C"], float), bool(d["maximize"])
    r, c = C.shape
    if ex is not None:
        ui.say("c_ex_intro", title=ui.T[f"tp_ex{ex}_t"])
        ui.say(f"tp_ex{ex}_s")
    ui.say("c_data")
    ui.table(mdf(C, [f"R{i + 1}" for i in range(r)], [f"C{j + 1}" for j in range(c)]))

    ui.head("as_rep", name=name)
    if r != c:
        ui.say("as_pad", r=r, c=c)
    res = hungarian(C, maximize=maximize)
    record_problem("assignment", scope, ex, d, dict(
        assignment=[None if j is None else j + 1 for j in res.assignment], total=res.cost, maximize=maximize,
        padded=res.padded, unassigned_columns=[j + 1 for j in res.unassigned_cols], rows=r, columns=c))
    ui.say("as_h_title")
    ui.say("as_h_note")
    n = max(r, c)
    rl = [f"R{i + 1}" for i in range(n)]
    cl = [f"C{j + 1}" for j in range(n)]
    k = 0
    for stp in res.steps:
        if stp.kind == "row":
            ui.say("as_h_row")
        elif stp.kind == "col":
            ui.say("as_h_col")
        elif stp.kind == "adjust":
            k += 1
            ui.say("as_h_adj", k=k, a=stp.matched, d=stp.delta)
        else:
            ui.say("as_h_done", n=n, kind="ok")
            continue
        ui.table(mdf(stp.matrix, rl, cl))

    ui.say("as_res_hdr")
    rows, lines = [], []
    for i, j in enumerate(res.assignment):
        if j is None:
            lines.append(ui.s("as_res_dummy", i=i + 1))
            rows.append((f"R{i + 1}", "-", ""))
        else:
            lines.append(ui.s("as_res_row", i=i + 1, j=j + 1, c=C[i, j]))
            rows.append((f"R{i + 1}", f"C{j + 1}", f"{C[i, j]:g}"))
    for j in res.unassigned_cols:
        lines.append(ui.s("as_res_free", j=j + 1))
    ui.raw("\n".join(lines))
    ui.say("as_tot_max" if maximize else "as_tot_min", c=res.cost, kind="ok")
    ui.download(pd.DataFrame(rows, columns=["row", "col", "value"]).set_index("row"), "assignment.csv", scope)
    if ex is not None:
        ui.say("c_ex_obs")
        ui.say(f"tp_ex{ex}_o")
    return True


# ==========================================================================
#                        PART 3: NON-LINEAR OPTIMIZATION
# ==========================================================================
METHOD_ORDER = ("golden", "fibonacci", "newton", "secant")


def nl_inputs(ui: UI) -> Optional[dict]:
    W = ui.W
    good = True
    text = st.text_input(ui.label("nl_ask_fun"), value=ui.T["nl_default_fun"], key="nl_text",
                         help=ui.tip("nl_ask_fun"))
    try:
        Objective(text, 1)
    except (ValueError, RuntimeError) as e:
        ui.say("nl_err_expr", e=e)
        good = False
    sign = st.radio(W["goal"], [1, -1], horizontal=True, key="nl_goal", help=ui.tip("nl_ask_goal"),
                    format_func=lambda v: W["mn"] if v == 1 else W["mx"])
    c1, c2, c3 = st.columns(3)
    a = float(c1.number_input(ui.label("nl_ask_a"), value=0.0, format="%g", key="nl_a", help=ui.tip("nl_ask_a")))
    b = float(c2.number_input(ui.label("nl_ask_b"), value=5.0, format="%g", key="nl_b", help=ui.tip("nl_ask_b")))
    tol_txt = c3.text_input(ui.label("nl_ask_tol"), value="1e-6", key="nl_tol",
                            help=(ui.tip("nl_ask_tol") or "") + "  " + W["tol_hint"])
    tol: Optional[float] = None
    try:
        tol = float(tol_txt)
        if not math.isfinite(tol):
            raise ValueError
        if not (1e-12 <= tol <= 1.0):
            ui.say("c_err_range", lo=1e-12, hi=1.0)
            good = False
    except ValueError:
        ui.say("c_err_number")
        tol, good = None, False
    if not a < b:
        ui.say("nl_err_interval")
        st.button(W["solve"], type="primary", key="nl_go", disabled=True)
        return None
    d1, d2 = st.columns(2)
    x0 = float(d1.number_input(ui.label("nl_ask_x0"), value=(a + b) / 2, format="%g", key=f"nl_x0_{a}_{b}",
                               help=ui.tip("nl_ask_x0")))
    alt = x0 + 0.1 * (b - a)
    x1 = float(d2.number_input(ui.label("nl_ask_x1"), value=alt if alt <= b else x0 - 0.1 * (b - a),
                               format="%g", key=f"nl_x1_{a}_{b}_{x0}", help=ui.tip("nl_ask_x1")))
    if not (a <= x0 <= b and a <= x1 <= b and x0 != x1):
        ui.say("nl_err_inside")
        good = False
    pressed = st.button(W["solve"], type="primary", key="nl_go", disabled=not good)
    if pressed and good:
        return dict(text=text, sign=sign, a=a, b=b, tol=tol, x0=x0, x1=x1)
    return None


def render_nlp(ui: UI, name: str, d: dict, ex: Optional[int], scope: str) -> bool:
    if sp is None:
        ui.say("c_no_sympy")
        return False
    ui.head("nl_title")
    obj = Objective(d["text"], d["sign"])
    a, b, tol, x0, x1 = d["a"], d["b"], d["tol"], d["x0"], d["x1"]
    if ex is not None:
        ui.say("c_ex_intro", title=ui.T[f"nl_ex{ex}_t"])
        ui.say(f"nl_ex{ex}_s")

    ui.head("nl_rep", name=name)
    ui.say("nl_fun", t=obj.text)
    ui.say("nl_d1", t=obj.df_text)
    ui.say("nl_d2", t=obj.d2f_text)
    ui.raw(f"[a, b] = [{a:g}, {b:g}] | tol = {tol:g} | x0 = {x0:g} | x1 = {x1:g}", mono=True)
    if not obj.symbolic:
        ui.say("nl_numeric")

    ui.head("nl_sec_diag")
    diag = diagnose(obj, a, b, x0, x1)
    lines = []
    for mth in METHOD_ORDER:
        okm, reason, params = diag[mth]
        lab = "nl_bypassed" if not okm else ("nl_caution" if reason == "uni_multimodal" else "nl_applicable")
        lines.append(f"{ui.s(lab)} {ui.s('nl_m_' + mth)}: {ui.s(reason, **params)}")
    ui.raw("\n".join(lines))

    ui.head("nl_sec_res")
    results = []
    for mth in METHOD_ORDER:
        if not diag[mth][0]:
            continue
        r = run_method(obj, mth, a, b, x0, x1, tol)
        results.append(r)
        block = [ui.s("nl_res", m=ui.s("nl_m_" + mth), x=r.x, fx=obj.user_value(r.fx), it=r.iterations, ev=r.evals),
                 ui.s("nl_status", s=ui.s("st_" + r.status))]
        block += [ui.s("n_" + code, **params) for code, params in r.notes]
        ui.raw("\n".join(block), kind="ok" if r.status == "converged" else "warn")
        if ui.detail and r.history:
            with st.expander(f"{ui.title_of('nl_m_' + mth)} - {ui.W['hist']}", expanded=False):
                ui.say("nl_table")
                keys = list(r.history[0].keys())
                rows = r.history if len(r.history) <= 40 else r.history[:20] + r.history[-20:]
                df = pd.DataFrame([[str(h[k]) if k == "k" else f"{h[k]:.6g}" for k in keys] for h in rows],
                                  columns=keys)
                ui.table(df.set_index("k") if "k" in df.columns else df)
                if len(r.history) > 40:
                    st.caption(ui.W["omitted_rows"].format(k=len(r.history) - 40))

    ui.head("nl_sec_ver")
    gx, gf = grid_minimum(obj.f, a, b)
    ui.say("nl_grid", x=gx, fx=obj.user_value(gf))
    good = [r for r in results if r.status == "converged"]
    record_problem("nonlinear", scope, ex, d, dict(
        function=obj.text, goal="max" if d["sign"] == -1 else "min",
        methods=[dict(method=r.method, status=r.status, x=r.x, value=obj.user_value(r.fx),
                      iterations=r.iterations, evaluations=r.evals) for r in results],
        bypassed=[m for m in METHOD_ORDER if not diag[m][0]], grid_x=gx, grid_value=obj.user_value(gf)))
    if not good:
        ui.say("nl_none")
        return False
    best = min(good, key=lambda r: r.fx)
    ui.say("nl_best", m=ui.s("nl_m_" + best.method), x=best.x, fx=obj.user_value(best.fx))
    verified = best.fx <= gf + 1e-6 * (1.0 + abs(gf))
    ui.say("nl_agree" if verified else "nl_worse")

    if ui.plot and plt is not None:
        with st.expander(ui.W["curve"], expanded=True):
            fig = plot_nlp_1d(obj, a, b, best.x, lang=ui.lang, title=obj.text, show=False, return_fig=True)
            st.pyplot(fig)
            plt.close(fig)
    if ex is not None:
        ui.say("c_ex_obs")
        ui.say(f"nl_ex{ex}_o")
    return verified


# ==========================================================================
#                              PAGES / NAVIGATION
# ==========================================================================
PARTS = {
    1: dict(title="lp_name", ex_menu="lp_ex_menu", prefix="lp", learn="lp_learn"),
    2: dict(title="tp_name", ex_menu="tp_ex_menu", prefix="tp", learn="tp_learn"),
    3: dict(title="nl_name", ex_menu="nl_ex_menu", prefix="nl", learn="nl_learn"),
}
PAGES = ["home", "part1", "part2", "part3", "guide", "selftest", "about"]


def execute(ui: UI, part: int, fn, d: dict, ex: Optional[int], name: str, scope: str) -> None:
    """Run a renderer with the same safety net as the console ``_run_safely``."""
    try:
        ok = bool(fn(ui, name, d, ex, scope))
    except (ValueError, RuntimeError, ArithmeticError, np.linalg.LinAlgError) as e:
        ui.say("c_error", e=e, kind="err")
        ok = False
    ui.raw(ui.s("c_ft", part=ui.T[PARTS[part]["title"]], status=ui.s("c_ft_ok" if ok else "c_ft_fail")),
           kind="ok" if ok else "warn")


def snapshot_gate(scope: str, fresh: Optional[dict]) -> Optional[dict]:
    """Keep the data of the last 'Solve' click so results survive widget reruns."""
    if fresh is not None:
        st.session_state[f"snap::{scope}"] = fresh
    return st.session_state.get(f"snap::{scope}")


def page_part(ui: UI, part: int, name: str) -> None:
    info = PARTS[part]
    short = ui.short(ui.T[f"c_p{part}_title"])
    st.header(short)
    ui.raw(ui.T[f"c_p{part}_sum"])
    modes = {"own": "c_sub_own", "ex": "c_sub_ex", "learn": "c_sub_learn"}
    mode = st.radio(ui.s("c_sub_title", part=short), list(modes), horizontal=True, key=f"mode_{part}",
                    format_func=lambda k: ui.short(ui.T[modes[k]]))
    st.divider()

    if mode == "learn":
        ui.raw(ui.s(info["learn"]), mono=(ui.lang == "en"))
        return

    if mode == "own":
        if part == 1:
            scope, fn, fresh = "p1_own", render_lp, lp_inputs(ui)
        elif part == 3:
            if sp is None:
                ui.say("c_no_sympy")
                return
            scope, fn, fresh = "p3_own", render_nlp, nl_inputs(ui)
        else:
            kind = st.radio(ui.W["kind"], ["tp", "as"], horizontal=True, key="tp_kind",
                            help=ui.tip("tp_ask_kind"),
                            format_func=lambda k: ui.W["transport"] if k == "tp" else ui.W["assign"])
            if kind == "tp":
                scope, fn, fresh = "p2_tp_own", render_transport, tp_inputs(ui)
            else:
                scope, fn, fresh = "p2_as_own", render_assignment, as_inputs(ui)
        data = snapshot_gate(scope, fresh)
        if data is not None:
            st.divider()
            execute(ui, part, fn, data, None, name, scope)
        return

    # ---- worked example ------------------------------------------------------
    ui.raw(ui.s(info["ex_menu"]), mono=True)
    prefix = info["prefix"]
    pick = st.selectbox(ui.W["example"], list(EXAMPLE_RANGE[part]), key=f"ex_pick_{part}",
                        format_func=lambda k: f"[{k}] {ui.T[f'{prefix}_ex{k}_t']}")
    scope = f"p{part}_ex{pick}"
    fresh = dict(ex=pick) if st.button(ui.W["run_ex"], type="primary", key=f"run_ex_{part}") else None
    if snapshot_gate(scope, fresh) is None:
        return
    st.divider()
    if part == 1:
        execute(ui, part, render_lp, dict(LP_EXAMPLES[pick], method="auto"), pick, name, scope)
    elif part == 3:
        execute(ui, part, render_nlp, NL_EXAMPLES[pick], pick, name, scope)
    elif pick >= 3:
        execute(ui, part, render_assignment, AS_EXAMPLES[pick], pick, name, scope)
    else:
        execute(ui, part, render_transport, TP_EXAMPLES[pick], pick, name, scope)


def page_home(ui: UI, name: str) -> None:
    welcome = re.split(r"(?:Tip:|تلميح:)", ui.s("c_welcome", name=name))[0]
    ui.raw(welcome + " " + ui.W["web_tip"])
    ui.head("c_menu_title")

    def go(page):
        st.session_state["page"] = page

    for p, col in zip((1, 2, 3), st.columns(3)):
        with col:
            with st.container(border=True):
                st.markdown(f"**{ui.T[f'c_p{p}_title']}**")
                ui.raw(ui.T[f"c_p{p}_sum"])
                st.button("→", key=f"home_go_{p}", on_click=go, args=(f"part{p}",))


def page_guide(ui: UI) -> None:
    st.header(ui.short(ui.T["c_m_guide"]))
    ui.raw(ui.s("c_guide"), mono=(ui.lang == "en"))


def page_about(ui: UI) -> None:
    st.header(ui.short(ui.T["c_m_about"]))
    ui.raw(ui.s("c_about", ver=__version__, author=AUTHOR, copyright=COPYRIGHT, license=LICENSE, url=REPOSITORY))


def page_selftest(ui: UI) -> None:
    st.header(ui.short(ui.T["c_m_test"]))
    if st.button(ui.W["run_test"], type="primary", key="run_selftest"):
        with st.spinner(ui.W["spin"]):
            st.session_state["selftest"] = run_selftest()
    results = st.session_state.get("selftest")
    if results is None:
        return
    ui.head("c_st_hdr")
    rows, passed, total = [], 0, 0
    for label, r in results:
        tag = ui.s("c_st_skip") if r is None else ui.s("c_st_pass") if r else ui.s("c_st_fail")
        rows.append((tag, label))
        if r is not None:
            total += 1
            passed += bool(r)
    ui.table(pd.DataFrame(rows, columns=["", "check"]).set_index(""))
    ui.say("c_st_sum", p=passed, t=total, kind="ok" if passed == total else "err")


def _on_lang_change() -> None:
    """Keep the default analyst name in sync with the language (as the console does)."""
    defaults = {TEXT["en"]["c_default_name"], TEXT["ar"]["c_default_name"]}
    if st.session_state.get("name") in defaults:
        st.session_state["name"] = TEXT[st.session_state["lang"]]["c_default_name"]


def _init_state() -> None:
    qp = {}
    try:
        qp = dict(st.query_params)
    except Exception:                                    # old Streamlit: no query_params
        pass
    if "lang" not in st.session_state:
        st.session_state["lang"] = qp["lang"] if qp.get("lang") in ("en", "ar") else "en"
    if "page" not in st.session_state:
        st.session_state["page"] = qp["page"] if qp.get("page") in PAGES else "home"
    if "name" not in st.session_state:
        st.session_state["name"] = TEXT[st.session_state["lang"]]["c_default_name"]


def main(configure_page: bool = True) -> None:
    if configure_page:
        st.set_page_config(**PAGE_CONFIG)
    _init_state()
    st.sidebar.selectbox(WEB["en"]["lang"], ["en", "ar"], key="lang", on_change=_on_lang_change,
                         format_func=lambda k: "English" if k == "en" else "العربية")
    lang = st.session_state["lang"]
    st.markdown(CSS + (CSS_RTL if lang == "ar" else ""), unsafe_allow_html=True)
    detail = st.sidebar.checkbox(WEB[lang]["detail"], value=False, key="detail")
    plot = st.sidebar.checkbox(WEB[lang]["plot"], value=True, key="plot")
    ui = UI(lang, detail, plot)
    if detail:
        record_flag("detail_mode_used")

    st.sidebar.text_input(ui.label("c_ask_name"), key="name")
    names = {"home": ui.W["home"],
             "part1": ui.short(ui.T["c_p1_title"]), "part2": ui.short(ui.T["c_p2_title"]),
             "part3": ui.short(ui.T["c_p3_title"]), "guide": ui.short(ui.T["c_m_guide"]),
             "selftest": ui.short(ui.T["c_m_test"]), "about": ui.short(ui.T["c_m_about"])}
    st.sidebar.radio(ui.W["nav"], PAGES, key="page", format_func=lambda k: names[k])
    st.sidebar.caption(f"v{__version__} | {COPYRIGHT} | {LICENSE}")

    # banner (same lines as the console banner)
    st.markdown(f'<div class="oa-title">OPTIARCHITECT  v{__version__}  |  '
                f'OPERATIONS RESEARCH &amp; OPTIMIZATION TOOLKIT</div>'
                f'<div class="oa-sub">{html.escape(ui.W["banner2"])}</div>'
                f'<div class="oa-sub">{html.escape(ui.W["dev"])}: {html.escape(AUTHOR)} · '
                f'{html.escape(COPYRIGHT)} · {html.escape(LICENSE)}</div>', unsafe_allow_html=True)
    st.divider()

    name = (st.session_state.get("name") or "").strip() or ui.T["c_default_name"]
    page = st.session_state["page"]
    record_page(page)
    if page == "home":
        page_home(ui, name)
    elif page in ("part1", "part2", "part3"):
        page_part(ui, int(page[-1]), name)
    elif page == "guide":
        page_guide(ui)
    elif page == "selftest":
        page_selftest(ui)
    else:
        page_about(ui)


if __name__ == "__main__":          # `streamlit run app.py` executes the script as __main__
    main()
