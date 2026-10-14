#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiArchitect - participant-facing STUDY application (Streamlit).

Flow:  questionnaire 1 (consent, profile, status, confidence, difficulties)
       -> the normal OptiArchitect web application (every problem the student runs is logged)
       -> questionnaire 2 (SUS, usefulness, features, overall) -> report saved in ``study_data/``.

Run (from the folder in which ``study_data/`` should be created):

    optiarchitect-study               # or: streamlit run src/optiarchitect/study/app_study.py

The researcher reads the reports with ``optiarchitect-study-admin`` or directly in ``study_data/``.
Configuration (researcher name/e-mail, ethics reference, data folder, optional e-mail copy) is read from
environment variables; see docs/study.md.
"""
import json
import time

import streamlit as st

from optiarchitect import app as oa
from optiarchitect.study import forms, instruments as I
from optiarchitect.study.settings import CONSENT_VERSION, StudySettings
from optiarchitect.study.storage import (StudyStore, new_record, render_report_html, send_report,
                                         split_pre_answers, utc_now)
from optiarchitect.study.texts import T, info_lines

CSS = """<style>
.block-container{max-width:1100px}
div[data-testid="stForm"]{border:1px solid rgba(128,128,128,.35);border-radius:8px;padding:1.2rem}
h4{margin-top:1.6rem;border-bottom:1px solid rgba(128,128,128,.35);padding-bottom:.25rem}
</style>"""


def _lang() -> str:
    return st.session_state.get("study_lang_value", "en")


def _head(step: int, settings: StudySettings, key: str) -> str:
    """Language selector, progress bar and study title; returns the active language."""
    choice = st.radio("Language / اللغة", ["en", "ar"], index=["en", "ar"].index(_lang()), horizontal=True,
                      key=f"study_lang_widget_{key}", format_func=lambda k: "English" if k == "en" else "العربية")
    st.session_state["study_lang_value"] = choice
    t = T[choice]
    st.markdown(CSS + (oa.CSS_RTL if choice == "ar" else ""), unsafe_allow_html=True)
    st.progress(step / 3)
    st.caption(t["step"].format(i=step, n=3) + " - " + t["steps"][step - 1])
    st.markdown(f"##### {settings.title_ar if choice == 'ar' else settings.title}")
    return choice


def _show_errors(errors, lang):
    t = T[lang]
    st.error(t["errors_head"].format(n=len(errors)) + "\n\n" + "\n".join(f"- {e}" for e in errors))


def _save(store: StudyStore, rec: dict, lang: str) -> bool:
    """Save the record; on a disk problem keep the student's work and offer a downloadable copy."""
    try:
        store.save(rec)
        return True
    except OSError:
        st.error(T[lang]["save_error"])
        st.download_button("JSON", json.dumps(rec, ensure_ascii=False, indent=2).encode("utf-8"),
                           file_name=f"{rec['participant_id']}.json", mime="application/json", key="study_fallback_dl")
        return False


# ------------------------------------------------------------------------------------------ stage 1
def stage_pre(settings: StudySettings, store: StudyStore) -> None:
    rec = st.session_state["study_record"]
    _, mid, _ = st.columns([1, 6, 1])
    with mid:
        lang = _head(1, settings, "pre")
        t = T[lang]
        st.markdown(f"## {t['thanks_title']}")
        st.markdown(t["thanks"])
        with st.expander(t["info_title"], expanded=True):
            for line in info_lines(lang, settings):
                st.markdown(line)
        st.markdown(f"### {t['pre_title']}")
        st.caption(t["required_note"])
        with st.form("study_pre_form"):
            answers = forms.render_sections(I.PRE_SECTIONS, lang, "pre")
            submitted = st.form_submit_button(t["pre_submit"], type="primary")
        if not submitted:
            return
        errors = forms.validate(I.PRE_SECTIONS, answers, lang)
        if errors:
            _show_errors(errors, lang)
            return
        consent, participant, pre = split_pre_answers(answers)
        rec.update(language=lang, consent=dict(consent, timestamp=utc_now(), version=CONSENT_VERSION),
                   participant=participant, pre=pre, status="pre_completed")
        rec["timestamps"]["pre_submitted"] = utc_now()
        if not _save(store, rec, lang):
            return
        st.session_state.update(study_stage="tool", study_tool_started=time.time(), study_active=True,
                                study_problems={}, study_pages=[], study_flags={}, lang=lang,
                                name=(participant["full_name"].split() or [""])[0], page="home")
        st.rerun()


# ------------------------------------------------------------------------------------------ stage 2
def _finish_tool(store: StudyStore) -> None:
    rec = st.session_state["study_record"]
    rec["problems"] = sorted(st.session_state.get("study_problems", {}).values(), key=lambda p: p["first_seen"])
    rec["usage"] = {"seconds": round(time.time() - st.session_state.get("study_tool_started", time.time())),
                    "pages": list(st.session_state.get("study_pages", [])),
                    "flags": dict(st.session_state.get("study_flags", {}))}
    rec["status"] = "tool_completed"
    rec["timestamps"]["tool_finished"] = utc_now()
    st.session_state["study_lang_value"] = st.session_state.get("lang", _lang())
    st.session_state["study_active"] = False
    st.session_state["study_stage"] = "post"
    try:
        store.save(rec)
    except OSError:
        pass                                  # the post stage saves again and reports a failure to the student


def _withdraw(store: StudyStore) -> None:
    pid = st.session_state["study_record"]["participant_id"]
    try:
        store.delete(pid)
    except (OSError, ValueError):
        pass
    for k in ("study_problems", "study_pages", "study_flags", "study_record"):
        st.session_state.pop(k, None)
    st.session_state["study_active"] = False
    st.session_state["study_stage"] = "withdrawn"


def stage_tool(settings: StudySettings, store: StudyStore) -> None:
    st.session_state["study_active"] = True
    lang = st.session_state.get("lang", _lang())
    t = T[lang]
    st.info(t["step"].format(i=2, n=3) + " - " + t["steps"][1] + ": " + t["sidebar_need"].format(m=settings.min_problems))
    oa.main(configure_page=False)
    lang = st.session_state.get("lang", lang)
    t = T[lang]
    rec = st.session_state["study_record"]
    n = len(st.session_state.get("study_problems", {}))
    sb = st.sidebar
    sb.divider()
    sb.markdown(f"**{t['sidebar_title']}**")
    sb.caption(f"{t['sidebar_code']}: {rec['participant_id']}")
    sb.markdown(t["sidebar_count"].format(n=n))
    if n < settings.min_problems:
        sb.caption(t["sidebar_need"].format(m=settings.min_problems))
    sb.button(t["finish"], key="study_finish", type="primary", disabled=n < settings.min_problems,
              on_click=_finish_tool, args=(store,))
    with sb.expander(t["withdraw_title"]):
        ok = st.checkbox(t["withdraw_confirm"], key="study_withdraw_ok")
        st.button(t["withdraw_button"], key="study_withdraw", disabled=not ok, on_click=_withdraw, args=(store,))


# ------------------------------------------------------------------------------------------ stage 3
def stage_post(settings: StudySettings, store: StudyStore) -> None:
    rec = st.session_state["study_record"]
    _, mid, _ = st.columns([1, 6, 1])
    with mid:
        lang = _head(3, settings, "post")
        t = T[lang]
        st.markdown(f"## {t['post_title']}")
        st.markdown(t["post_intro"])
        st.caption(t["required_note"])
        with st.form("study_post_form"):
            answers = forms.render_sections(I.POST_SECTIONS, lang, "post")
            submitted = st.form_submit_button(t["post_submit"], type="primary")
        if not submitted:
            return
        errors = forms.validate(I.POST_SECTIONS, answers, lang)
        if errors:
            _show_errors(errors, lang)
            return
        rec.update(post=answers, status="completed")
        rec["timestamps"]["post_submitted"] = utc_now()
        if not _save(store, rec, lang):
            return
        if settings.email_enabled:                   # optional copy by e-mail; the data are already on disk
            ok, msg = send_report(settings, rec, render_report_html(rec))
            rec["delivery"]["email"] = msg
            _save(store, rec, lang)
        st.session_state["study_stage"] = "done"
        st.rerun()


# ------------------------------------------------------------------------------------------ end pages
def stage_done(settings: StudySettings, store: StudyStore) -> None:
    rec = st.session_state["study_record"]
    _, mid, _ = st.columns([1, 6, 1])
    with mid:
        lang = _lang()
        t = T[lang]
        st.markdown(CSS + (oa.CSS_RTL if lang == "ar" else ""), unsafe_allow_html=True)
        st.progress(1.0)
        st.markdown(f"## {t['done_title']}")
        st.markdown(t["done_text"].format(pid=rec["participant_id"]))
        st.download_button(t["done_copy"], json.dumps(rec, ensure_ascii=False, indent=2).encode("utf-8"),
                           file_name=f"{rec['participant_id']}.json", mime="application/json", key="study_copy_dl")


def stage_withdrawn(settings: StudySettings, store: StudyStore) -> None:
    lang = _lang()
    st.markdown(CSS + (oa.CSS_RTL if lang == "ar" else ""), unsafe_allow_html=True)
    st.success(T[lang]["withdrawn"])


STAGES = {"pre": stage_pre, "tool": stage_tool, "post": stage_post, "done": stage_done, "withdrawn": stage_withdrawn}


def run(env=None) -> None:
    st.set_page_config(page_title="OptiArchitect study", page_icon="🎓", layout="wide")
    settings = StudySettings.from_env(env)
    store = StudyStore(settings.data_dir)
    if "study_stage" not in st.session_state:
        st.session_state["study_record"] = new_record(settings, "en")
        st.session_state["study_stage"] = "pre"
    STAGES[st.session_state["study_stage"]](settings, store)


if __name__ == "__main__":
    run()
