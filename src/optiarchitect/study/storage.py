"""
Storage of study data and generation of the per-participant report.

Layout (inside ``StudySettings.data_dir``, by default ``./study_data`` next to the program)::

    study_data/
      README.txt                 what is stored and how to handle it
      master.csv                 one row per participant (rebuilt after every save; opens in Excel)
      participants/
        OA-20261012-3fa9c1.json  complete machine-readable record
        OA-20261012-3fa9c1.html  human-readable report (open it in any browser)

Security notes: file names are generated here (never taken from user input); every text typed by the
participant is HTML-escaped in the report; CSV cells that could be read as spreadsheet formulas are
neutralised; the data directory must never be committed to a public repository (it is in .gitignore).
"""
import csv
import html
import io
import json
import os
import re
import secrets
import smtplib
import ssl
import tempfile
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import streamlit as st
from supabase import create_client

supabase_url = st.secrets.get("SUPABASE_URL")
supabase_key = st.secrets.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

from optiarchitect.config import __version__
from optiarchitect.study import instruments as I
from optiarchitect.study.scoring import confidence_change, derived_metrics
from optiarchitect.study.settings import CONSENT_VERSION, StudySettings

ID_RE = re.compile(r"^OA-\d{8}-[0-9a-f]{6}$")
PROFILE_IDS = ("full_name", "university", "college", "department", "course", "instructor", "level")
CONSENT_IDS = tuple(i.id for i in I.CONSENT_ITEMS)
KIND_LABEL = {"lp": "Linear programming", "transportation": "Transportation", "assignment": "Assignment (Hungarian)",
              "nonlinear": "Non-linear, one variable"}
README_TEXT = """OptiArchitect study data
========================
This folder contains personal data of study participants (names, institutions, answers).
* Do NOT publish it, commit it to a public repository, or share it beyond the research team.
* participants/<id>.json is the complete record; participants/<id>.html is the readable report.
* master.csv is rebuilt automatically from the .json files (UTF-8 with BOM, opens in Excel).
* A participant who asks to be removed can be deleted from the admin application (or delete both files).
* Keep a back-up: if the program runs on a hosting service with temporary disk, download the data regularly.
"""


# ------------------------------------------------------------------------------------------------ basics
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_participant_id(now: Optional[datetime] = None) -> str:
    now = now or datetime.now(timezone.utc)
    return f"OA-{now:%Y%m%d}-{secrets.token_hex(3)}"


def new_record(settings: StudySettings, lang: str, pid: Optional[str] = None) -> dict:
    return {
        "schema_version": 1, "software_version": __version__, "participant_id": pid or new_participant_id(),
        "status": "started", "language": lang,
        "study": {"title": settings.title, "researcher": settings.researcher, "institution": settings.institution,
                  "consent_version": CONSENT_VERSION, "ethics_ref": settings.ethics_ref},
        "timestamps": {"started": utc_now()}, "consent": {}, "participant": {}, "pre": {},
        "problems": [], "usage": {}, "post": {}, "derived": {}, "delivery": {},
    }


def split_pre_answers(answers: dict) -> Tuple[dict, dict, dict]:
    """Split the pre-questionnaire answers into (consent, participant, pre)."""
    consent = {k: bool(answers[k]) for k in CONSENT_IDS if k in answers}
    participant = {k: answers[k] for k in PROFILE_IDS if k in answers}
    pre = {k: v for k, v in answers.items() if k not in CONSENT_IDS and k not in PROFILE_IDS}
    return consent, participant, pre


def _atomic_write(path: Path, text: str, encoding: str = "utf-8") -> None:
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=path.suffix)
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ------------------------------------------------------------------------------------------------ answers -> text
def _items_by_id() -> Dict[str, I.Item]:
    return {i.id: i for i in I.all_items(I.PRE_SECTIONS) + I.all_items(I.POST_SECTIONS)}


def answer_text(item: I.Item, value) -> str:
    """Human-readable (English) form of a stored answer."""
    if value is None or value == "" or value == []:
        return "—"
    if item.kind == "likert":
        label = I.scale_label(item.scale, value, "en")
        # labels such as "4 - Very good" or "7" already contain the number: do not repeat it
        return label if label.startswith(str(value)) else f"{value} – {label}"
    if item.kind == "multi":
        return "; ".join(I.choice_label(item, v) for v in value)
    if item.kind == "single":
        return I.choice_label(item, value)
    if item.kind == "checkbox":
        return "Yes" if value else "No"
    return str(value)


# ------------------------------------------------------------------------------------------------ problem summaries
def _num(x, nd: int = 6) -> str:
    if isinstance(x, bool) or x is None:
        return "—" if x is None else str(x)
    if isinstance(x, (int, float)):
        return f"{x:.{nd}g}"
    if isinstance(x, list):
        return "[" + ", ".join(_num(v, nd) for v in x) + "]"
    return str(x)


def _lp_expr(row) -> str:
    parts = [(("-" if v < 0 else "+"), (f"{abs(v):g}*" if abs(v) != 1 else "") + f"x{j + 1}")
             for j, v in enumerate(row) if v != 0]
    if not parts:
        return "0"
    return ("-" if parts[0][0] == "-" else "") + parts[0][1] + "".join(f" {s} {t}" for s, t in parts[1:])


def problem_input_text(p: dict) -> str:
    d, kind = p.get("input", {}), p.get("kind")
    if kind == "lp":
        lines = [f"{d.get('obj', '?')} Z = {_lp_expr(d.get('c', []))}", "subject to"]
        lines += [f"  {_lp_expr(r)} {t} {b:g}" for r, t, b in zip(d.get("A", []), d.get("types", []), d.get("b", []))]
        return "\n".join(lines + ["  x >= 0"])
    if kind == "transportation":
        rows = ["  " + _num(r, 6) for r in d.get("C", [])]
        return "\n".join(["unit costs:"] + rows + [f"supply: {_num(d.get('S'))}", f"demand: {_num(d.get('D'))}"])
    if kind == "assignment":
        rows = ["  " + _num(r, 6) for r in d.get("C", [])]
        return "\n".join([("profit" if d.get("maximize") else "cost") + " matrix:"] + rows)
    if kind == "nonlinear":
        goal = "maximise" if d.get("sign") == -1 else "minimise"
        return (f"{goal} f(x) = {d.get('text')}  on [{_num(d.get('a'))}, {_num(d.get('b'))}]\n"
                f"tolerance {_num(d.get('tol'))}, start points x0 = {_num(d.get('x0'))}, x1 = {_num(d.get('x1'))}")
    return json.dumps(d, ensure_ascii=False)


def problem_result_text(p: dict) -> str:
    r, kind = p.get("result", {}), p.get("kind")
    if kind == "lp":
        return (f"method {r.get('method')} (requested: {r.get('requested_method')}); status {r.get('status')}; "
                f"Z = {_num(r.get('objective_value'))}; x = {_num(r.get('solution'))}; pivots {r.get('iterations')}; "
                f"max constraint violation {_num(r.get('max_violation'))}")
    if kind == "transportation":
        init = ", ".join(f"{k.upper()} {_num(v)}" for k, v in (r.get("initial_costs") or {}).items())
        return (f"dummy: {r.get('dummy') or 'none'}; start {str(r.get('start')).upper()}; initial costs [{init}]; "
                f"optimal cost {_num(r.get('optimal_cost'))}; MODI iterations {r.get('modi_iterations')}; "
                f"status {r.get('status')}; degeneracy repairs {r.get('degeneracy_repairs')}; "
                f"alternative optima {r.get('alternative_optima')}; residual {_num(r.get('max_residual'))}")
    if kind == "assignment":
        mapping = ", ".join(f"R{i + 1}->" + ("dummy" if j is None else f"C{j}") for i, j in enumerate(r.get("assignment", [])))
        return (f"{mapping}; total {_num(r.get('total'))}; padded {r.get('padded')}; "
                f"unassigned columns {r.get('unassigned_columns')}")
    if kind == "nonlinear":
        ms = "; ".join(f"{m.get('method')}: {m.get('status')}, x*={_num(m.get('x'))}, f={_num(m.get('value'))}, "
                       f"evals={m.get('evaluations')}" for m in r.get("methods", []))
        return f"{ms}; bypassed: {r.get('bypassed')}; grid scan x={_num(r.get('grid_x'))}, f={_num(r.get('grid_value'))}"
    return json.dumps(r, ensure_ascii=False)


# ------------------------------------------------------------------------------------------------ HTML report
_CSS = ("body{font-family:Arial,Helvetica,sans-serif;max-width:920px;margin:2rem auto;padding:0 1rem;color:#1b2631;line-height:1.45}"
        "h1{font-size:1.5rem}h2{font-size:1.15rem;border-bottom:1px solid #c9d1dc;padding-bottom:.2rem;margin-top:1.8rem}"
        "h3{font-size:1rem;margin-bottom:.2rem}table{border-collapse:collapse;width:100%;font-size:.92rem}"
        "td,th{border:1px solid #c9d1dc;padding:.35rem .5rem;vertical-align:top;text-align:left}th{background:#eef2f7}"
        "td.k{width:52%}pre{background:#f6f7f9;padding:.6rem;overflow:auto;font-size:.82rem;white-space:pre-wrap}"
        ".meta{color:#555;font-size:.9rem}.ok{color:#1b7a3d}.bad{color:#a12626}details{margin:.3rem 0}")


def _e(x) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def _table(rows: Iterable[Tuple[str, str]], head: Optional[Tuple[str, str]] = None) -> str:
    out = ["<table>"]
    if head:
        out.append(f"<tr><th>{_e(head[0])}</th><th>{_e(head[1])}</th></tr>")
    for k, v in rows:
        out.append(f'<tr><td class="k">{_e(k)}</td><td dir="auto">{_e(v)}</td></tr>')
    out.append("</table>")
    return "".join(out)


def _answers_block(sections, answers: dict) -> str:
    out = []
    for s in sections:
        if s.id in ("consent", "profile"):
            continue
        rows = [(it.en, answer_text(it, answers.get(it.id))) for it in s.items]
        out.append(f"<h3>{_e(s.en)}</h3>" + _table(rows))
    return "".join(out)


def render_report_html(record: dict) -> str:
    pid, ts, d = record["participant_id"], record.get("timestamps", {}), record.get("derived") or derived_metrics(record)
    part, usage = record.get("participant", {}), record.get("usage", {})
    items = _items_by_id()
    out = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Study report {_e(pid)}</title>'
           f"<style>{_CSS}</style></head><body>",
           f"<h1>OptiArchitect study report &mdash; {_e(pid)}</h1>",
           f'<p class="meta">Status: <b>{_e(record.get("status"))}</b> &middot; interface language: {_e(record.get("language"))}'
           f' &middot; software v{_e(record.get("software_version"))} &middot; consent form v{_e(record.get("study", {}).get("consent_version"))}'
           f'<br>Started {_e(ts.get("started"))} &middot; pre-questionnaire {_e(ts.get("pre_submitted", "—"))}'
           f' &middot; post-questionnaire {_e(ts.get("post_submitted", "—"))}'
           f' &middot; time in the tool: {_e(d.get("usage_minutes", "—"))} min</p>']

    labels = {"full_name": "Full name", "university": "University", "college": "College / faculty",
              "department": "Department", "course": "Course / module", "instructor": "Course instructor", "level": "Academic level"}
    rows = [(labels[k], answer_text(items[k], part.get(k)) if k in items else part.get(k, "—")) for k in PROFILE_IDS]
    out.append("<h2>1. Participant and institution (entered by the student)</h2>" + _table(rows))
    consent = record.get("consent", {})
    out.append("<h3>Consent</h3>" + _table([(items[k].en, "Yes" if consent.get(k) else "No") for k in CONSENT_IDS]))

    out.append("<h2>2. Answers before using the tool</h2>" + _answers_block(I.PRE_SECTIONS, record.get("pre", {})))

    out.append(f"<h2>3. Problems solved in the tool ({len(record.get('problems', []))})</h2>")
    if not record.get("problems"):
        out.append("<p>None recorded.</p>")
    for n, p in enumerate(record.get("problems", []), 1):
        source = f"worked example {p.get('example')}" if p.get("example") is not None else "own problem"
        out.append(f"<h3>{n}. {_e(KIND_LABEL.get(p.get('kind'), p.get('kind')))} &mdash; {_e(source)}"
                   f' <span class="meta">({_e(p.get("first_seen"))})</span></h3>'
                   f"<pre dir=\"auto\">{_e(problem_input_text(p))}</pre>"
                   f"<p dir=\"auto\"><b>Result:</b> {_e(problem_result_text(p))}</p>"
                   f"<details><summary>raw data (JSON)</summary><pre>{_e(json.dumps(p, ensure_ascii=False))}</pre></details>")

    out.append("<h2>4. How the tool was used</h2>" + _table([
        ("Pages visited", ", ".join(record.get("usage", {}).get("pages", [])) or "—"),
        ("Features used", ", ".join(k for k, v in (usage.get("flags") or {}).items() if v) or "—"),
        ("Time between the two questionnaires", f"{d.get('usage_minutes', '—')} min"),
        ("Problems run (own / worked examples)", f"{d.get('n_own_problems', 0)} / {d.get('n_example_problems', 0)}"),
    ]))

    out.append("<h2>5. Answers after using the tool</h2>" + _answers_block(I.POST_SECTIONS, record.get("post", {})))

    out.append("<h2>6. Computed scores</h2>")
    out.append(_table([
        ("System Usability Scale (0-100; about 68 is the commonly cited average)", _num(d.get("sus"))),
        ("Mean confidence before (1-5)", _num(d.get("confidence_pre_mean"))),
        ("Mean confidence after (1-5)", _num(d.get("confidence_post_mean"))),
        ("Mean change in confidence", _num(d.get("confidence_change_mean"))),
        ("Mean perceived usefulness (1-5)", _num(d.get("usefulness_mean"))),
    ]))
    ch = confidence_change(record.get("pre", {}), record.get("post", {}))
    rows = ["<table><tr><th>Task</th><th>Before</th><th>After</th><th>Change</th></tr>"]
    for (k, en, _ar), cid in zip(I.CONFIDENCE_ITEMS, I.CONFIDENCE_IDS):
        c = ch.get(cid)
        cls = "" if c is None else ("ok" if c > 0 else "bad" if c < 0 else "")
        rows.append(f"<tr><td>{_e(en)}</td><td>{_e(record.get('pre', {}).get(cid, '—'))}</td>"
                    f"<td>{_e(record.get('post', {}).get(cid, '—'))}</td><td class=\"{cls}\">{_e('—' if c is None else f'{c:+d}')}</td></tr>")
    out.append("".join(rows) + "</table>")
    if record.get("delivery"):
        out.append("<h2>7. Delivery</h2>" + _table([(k, v) for k, v in record["delivery"].items()]))
    out.append("</body></html>")
    return "".join(out)


# ------------------------------------------------------------------------------------------------ CSV
def _safe_cell(v):
    """Neutralise spreadsheet formula injection (a text cell starting with = + - @ is read as a formula)."""
    if isinstance(v, str) and v[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + v
    return v


def csv_columns() -> List[str]:
    pre_ids = [i.id for i in I.all_items(I.PRE_SECTIONS) if i.id not in PROFILE_IDS and i.id not in CONSENT_IDS]
    post_ids = [i.id for i in I.all_items(I.POST_SECTIONS)]
    return (["participant_id", "status", "language", "started", "pre_submitted", "post_submitted"] + list(PROFILE_IDS)
            + [f"pre_{i}" for i in pre_ids] + [f"post_{i}" for i in post_ids]
            + ["sus", "confidence_pre_mean", "confidence_post_mean", "confidence_change_mean", "usefulness_mean",
               "n_problems", "n_own_problems", "n_example_problems", "problem_kinds", "usage_minutes", "problems_json"])


def flat_row(record: dict) -> Dict[str, object]:
    d = record.get("derived") or derived_metrics(record)
    ts = record.get("timestamps", {})
    row: Dict[str, object] = {"participant_id": record["participant_id"], "status": record.get("status"),
                              "language": record.get("language"), "started": ts.get("started"),
                              "pre_submitted": ts.get("pre_submitted"), "post_submitted": ts.get("post_submitted")}
    row.update({k: record.get("participant", {}).get(k) for k in PROFILE_IDS})
    for k, v in record.get("pre", {}).items():
        row[f"pre_{k}"] = ";".join(v) if isinstance(v, list) else v
    for k, v in record.get("post", {}).items():
        row[f"post_{k}"] = ";".join(v) if isinstance(v, list) else v
    for k in ("sus", "confidence_pre_mean", "confidence_post_mean", "confidence_change_mean", "usefulness_mean",
              "n_problems", "n_own_problems", "n_example_problems", "usage_minutes"):
        row[k] = d.get(k)
    row["problem_kinds"] = ";".join(d.get("problem_kinds", []))
    row["problems_json"] = json.dumps(record.get("problems", []), ensure_ascii=False, separators=(",", ":"))
    return {k: _safe_cell(v) for k, v in row.items()}


def records_to_csv(records: Iterable[dict]) -> str:
    cols = csv_columns()
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore", lineterminator="\r\n")
    w.writeheader()
    for r in records:
        w.writerow(flat_row(r))
    return buf.getvalue()


# ------------------------------------------------------------------------------------------------ store
class StudyStore:
    def __init__(self, data_dir: Path):
        self.root = Path(data_dir)
        self.dir = self.root / "participants"
        self.dir.mkdir(parents=True, exist_ok=True)
        readme = self.root / "README.txt"
        if not readme.exists():
            _atomic_write(readme, README_TEXT)

    def _path(self, pid: str, ext: str) -> Path:
        if not ID_RE.match(pid or ""):
            raise ValueError("invalid participant id")
        return self.dir / f"{pid}{ext}"

    def save(self, record: dict) -> dict:
        record["derived"] = derived_metrics(record)
        pid = record["participant_id"]
        
        json_file_path = self._path(pid, ".json")
        html_file_path = self._path(pid, ".html")
        
        _atomic_write(json_file_path, json.dumps(record, ensure_ascii=False, indent=2))
        _atomic_write(html_file_path, render_report_html(record))
        
        self.rebuild_master()
        
        if supabase:
            try:
                with open(json_file_path, "rb") as f:
                    supabase.storage.from_("study_data").upload(
                        path=f"participants/{pid}.json",
                        file=f.read(),
                        file_options={"content-type": "application/json", "upsert": "true"}
                    )
                
                with open(html_file_path, "rb") as f:
                    supabase.storage.from_("study_data").upload(
                        path=f"participants/{pid}.html",
                        file=f.read(),
                        file_options={"content-type": "text/html", "upsert": "true"}
                    )
                
                master_path = self.root / "master.csv"
                if master_path.exists():
                    with open(master_path, "rb") as f:
                        supabase.storage.from_("study_data").upload(
                            path="master.csv",
                            file=f.read(),
                            file_options={"content-type": "text/csv", "upsert": "true"}
                        )
            except Exception as e:
                st.error(f"فشل الرفع السحابي: {e}")

        return record

    def load(self, pid: str) -> dict:
        return json.loads(self._path(pid, ".json").read_text(encoding="utf-8"))

    def records(self) -> List[dict]:
        out = []
        for p in sorted(self.dir.glob("OA-*.json")):
            if ID_RE.match(p.stem):
                try:
                    out.append(json.loads(p.read_text(encoding="utf-8")))
                except (OSError, ValueError):
                    continue
        return out

    def report_html(self, pid: str) -> str:
        return self._path(pid, ".html").read_text(encoding="utf-8")

    def delete(self, pid: str) -> bool:
        removed = False
        for ext in (".json", ".html"):
            p = self._path(pid, ext)
            if p.exists():
                p.unlink()
                removed = True
        self.rebuild_master()
        return removed

    def rebuild_master(self) -> Path:
        path = self.root / "master.csv"
        _atomic_write(path, records_to_csv(self.records()), encoding="utf-8-sig")
        return path


# ------------------------------------------------------------------------------------------------ e-mail (optional)
def build_email(settings: StudySettings, record: dict, report_html: str) -> EmailMessage:
    pid = record["participant_id"]
    d = record.get("derived", {})
    msg = EmailMessage()
    msg["Subject"] = f"[OptiArchitect study] completed report {pid}"
    msg["From"] = settings.smtp_from or settings.smtp_user or settings.email
    msg["To"] = settings.smtp_to or settings.email
    msg.set_content(
        f"A participant completed the OptiArchitect study.\n\nParticipant: {pid}\nProblems run: {d.get('n_problems')}\n"
        f"SUS: {d.get('sus')}\nMean confidence change: {d.get('confidence_change_mean')}\n\n"
        "The full report (HTML) and the complete record (JSON) are attached.\n")
    msg.add_attachment(report_html.encode("utf-8"), maintype="text", subtype="html", filename=f"{pid}.html")
    msg.add_attachment(json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8"),
                       maintype="application", subtype="json", filename=f"{pid}.json")
    return msg


def send_report(settings: StudySettings, record: dict, report_html: str) -> Tuple[bool, str]:
    """Send the completed report by e-mail. Never raises: the data are already safe on disk."""
    if not settings.email_enabled:
        return False, "e-mail not configured"
    try:
        msg = build_email(settings, record, report_html)
        ctx = ssl.create_default_context()
        if settings.smtp_ssl:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=ctx, timeout=20) as s:
                if settings.smtp_user:
                    s.login(settings.smtp_user, settings.smtp_password)
                s.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as s:
                s.starttls(context=ctx)
                if settings.smtp_user:
                    s.login(settings.smtp_user, settings.smtp_password)
                s.send_message(msg)
        return True, "sent"
    except Exception as exc:                      # network, authentication, TLS ... any failure
        return False, f"failed: {type(exc).__name__}: {exc}"
