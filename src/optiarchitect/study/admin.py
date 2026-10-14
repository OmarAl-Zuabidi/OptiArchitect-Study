#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiArchitect study - RESEARCHER dashboard (Streamlit, password protected).

    export OPTIARCHITECT_ADMIN_PASSWORD="choose-a-long-passphrase"
    optiarchitect-study-admin

Shows the participants, descriptive statistics, every per-participant report, and lets the researcher
download the data (master CSV, all reports as a ZIP) or delete a participant on request.
"""
import hmac
import io
import json
import zipfile

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from optiarchitect.study.scoring import derived_metrics
from optiarchitect.study.settings import StudySettings
from optiarchitect.study.storage import ID_RE, StudyStore, records_to_csv


def authorised(typed: str, expected: str) -> bool:
    """Constant-time password check; an unset password never authorises anybody."""
    return bool(expected) and hmac.compare_digest(typed.encode("utf-8"), expected.encode("utf-8"))


def overview_frame(records) -> pd.DataFrame:
    rows = []
    for r in records:
        d = r.get("derived") or derived_metrics(r)
        p = r.get("participant", {})
        rows.append({"participant": r["participant_id"], "status": r.get("status"), "language": r.get("language"),
                     "university": p.get("university"), "college": p.get("college"), "course": p.get("course"),
                     "instructor": p.get("instructor"), "problems": d.get("n_problems"), "SUS": d.get("sus"),
                     "conf_pre": d.get("confidence_pre_mean"), "conf_post": d.get("confidence_post_mean"),
                     "conf_change": d.get("confidence_change_mean"), "usefulness": d.get("usefulness_mean"),
                     "minutes": d.get("usage_minutes")})
    return pd.DataFrame(rows)


def describe(df: pd.DataFrame) -> dict:
    """Descriptive statistics of the completed participants (and paired tests when SciPy is installed)."""
    done = df[df["status"] == "completed"]
    out = {"n_completed": int(len(done))}
    for col in ("SUS", "conf_pre", "conf_post", "conf_change", "usefulness", "minutes"):
        s = pd.to_numeric(done[col], errors="coerce").dropna()
        out[col] = {"n": int(len(s)), "mean": float(s.mean()) if len(s) else None,
                    "sd": float(s.std(ddof=1)) if len(s) > 1 else None}
    pair = done[["conf_pre", "conf_post"]].apply(pd.to_numeric, errors="coerce").dropna()
    out["paired_tests"] = None
    if len(pair) >= 5:
        try:
            from scipy import stats
            t = stats.ttest_rel(pair["conf_post"], pair["conf_pre"])
            w = stats.wilcoxon(pair["conf_post"], pair["conf_pre"]) if (pair["conf_post"] != pair["conf_pre"]).any() else None
            out["paired_tests"] = {"n": int(len(pair)), "t": float(t.statistic), "p_t": float(t.pvalue),
                                   "p_wilcoxon": None if w is None else float(w.pvalue)}
        except ImportError:
            out["paired_tests"] = "scipy not installed"
    return out


def zip_everything(store: StudyStore) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(store.root / "master.csv", "master.csv")
        for p in sorted(store.dir.glob("OA-*")):
            if ID_RE.match(p.stem):
                z.write(p, f"participants/{p.name}")
    return buf.getvalue()


def run(env=None) -> None:
    st.set_page_config(page_title="OptiArchitect study - researcher", page_icon="🔒", layout="wide")
    settings = StudySettings.from_env(env)
    st.title("OptiArchitect study - researcher dashboard")
    if not settings.admin_password:
        st.error("Set the environment variable OPTIARCHITECT_ADMIN_PASSWORD to enable this page.")
        st.stop()
    if not authorised(st.text_input("Password", type="password", key="admin_pw"), settings.admin_password):
        st.info("Enter the password to continue.")
        st.stop()

    store = StudyStore(settings.data_dir)
    records = store.records()
    df = overview_frame(records)
    c1, c2, c3 = st.columns(3)
    c1.metric("Participants (any status)", len(records))
    c2.metric("Completed", int((df["status"] == "completed").sum()) if len(df) else 0)
    c3.metric("Data folder", str(store.root))
    if not records:
        st.info("No participant data yet.")
        st.stop()

    st.subheader("Participants")
    st.dataframe(df)
    d = describe(df)
    st.subheader("Descriptive statistics (completed participants)")
    st.json(d)
    st.caption("SUS: about 68 is the commonly cited average (Sauro, 2011). Confidence items are not a validated scale: "
               "treat the change as exploratory. Paired tests need at least 5 completed participants and SciPy.")

    st.subheader("Downloads")
    st.download_button("master.csv", records_to_csv(records).encode("utf-8-sig"), file_name="master.csv", mime="text/csv", key="dl_csv")
    st.download_button("All data (ZIP)", zip_everything(store), file_name="study_data.zip", mime="application/zip", key="dl_zip")

    st.subheader("Individual report")
    pid = st.selectbox("Participant", [r["participant_id"] for r in records], key="admin_pid")
    components.html(store.report_html(pid), height=700, scrolling=True)
    st.download_button("This record (JSON)", json.dumps(store.load(pid), ensure_ascii=False, indent=2).encode("utf-8"),
                       file_name=f"{pid}.json", mime="application/json", key="dl_json")

    with st.expander("Delete this participant (data-subject request)"):
        typed = st.text_input("Type the participant code to confirm", key="admin_del")
        if st.button("Delete permanently", key="admin_del_btn", disabled=typed != pid):
            store.delete(pid)
            st.success(f"{pid} deleted.")


if __name__ == "__main__":
    run()
