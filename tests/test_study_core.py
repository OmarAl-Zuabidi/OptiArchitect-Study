"""Instruments, scoring and storage of the student study (no browser needed)."""
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from optiarchitect.study import instruments as I
from optiarchitect.study import scoring as S
from optiarchitect.study import storage as ST
from optiarchitect.study.settings import StudySettings
from optiarchitect.study.texts import T

ARABIC = re.compile(r"[\u0600-\u06FF]")


def sample_record(**over):
    pre = {i.id: (i.choices[0].value if i.kind == "single" else [i.choices[0].value] if i.kind == "multi" else 3)
           for i in I.all_items(I.PRE_SECTIONS) if i.kind in ("single", "multi", "likert")
           and i.id not in ST.PROFILE_IDS}
    post = {i.id: (i.choices[0].value if i.kind == "single" else [i.choices[0].value] if i.kind == "multi" else 4)
            for i in I.all_items(I.POST_SECTIONS) if i.kind in ("single", "multi", "likert")}
    rec = ST.new_record(StudySettings(), "en")
    rec.update(status="completed", pre=pre, post=post,
               participant=dict(full_name="Ahmed Ali", university="Al-Nahrain University", college="Science",
                                department="Math", course="Operations Research", instructor="Dr. X", level="y3"),
               consent={k: True for k in ST.CONSENT_IDS},
               problems=[dict(kind="lp", scope="p1_ex1", example=1, first_seen="2026-10-12T10:00:00+00:00",
                              input=dict(c=[3, 5], A=[[1, 0], [0, 2], [3, 2]], b=[4, 12, 18], types=["<="] * 3, obj="max",
                                         method="auto"),
                              result=dict(method="standard", requested_method="auto", status="optimal", objective_value=36.0,
                                          solution=[2.0, 6.0], iterations=2, max_violation=0.0))],
               usage=dict(seconds=600, pages=["home", "part1"], flags={"detail_mode_used": True}))
    rec["timestamps"].update(pre_submitted="2026-10-12T09:50:00+00:00", post_submitted="2026-10-12T10:10:00+00:00")
    rec.update(over)
    return rec


class Instruments(unittest.TestCase):
    def test_every_text_exists_in_both_languages(self):
        for sections in (I.PRE_SECTIONS, I.POST_SECTIONS):
            for s in sections:
                self.assertTrue(s.en and s.ar, s.id)
                for it in s.items:
                    self.assertTrue(it.en.strip() and it.ar.strip(), it.id)
                    self.assertRegex(it.ar, ARABIC, it.id)
                    for c in it.choices:
                        self.assertTrue(c.en.strip() and c.ar.strip() and c.value, (it.id, c.value))
        for sc, rows in I.SCALES.items():
            for v, en, ar in rows:
                self.assertTrue(en and ar)

    def test_ids_choices_and_scales_are_consistent(self):
        for sections in (I.PRE_SECTIONS, I.POST_SECTIONS):
            ids = [i.id for i in I.all_items(sections)]
            self.assertEqual(len(ids), len(set(ids)))
            for it in I.all_items(sections):
                if it.kind in ("single", "multi"):
                    self.assertGreaterEqual(len(it.choices), 2, it.id)
                    values = [c.value for c in it.choices]
                    self.assertEqual(len(values), len(set(values)), it.id)
                    if it.exclusive:
                        self.assertIn(it.exclusive, values, it.id)
                if it.kind == "likert":
                    self.assertIn(it.scale, I.SCALES, it.id)

    def test_confidence_block_is_identical_before_and_after(self):
        pre = [i.id for s in I.PRE_SECTIONS if s.id == "confidence" for i in s.items]
        post = [i.id for s in I.POST_SECTIONS if s.id == "confidence" for i in s.items]
        self.assertEqual(pre, post)
        self.assertEqual(tuple(pre), I.CONFIDENCE_IDS)

    def test_requested_profile_fields_exist(self):
        ids = {i.id for i in I.all_items(I.PRE_SECTIONS)}
        for needed in ("full_name", "university", "college", "department", "course", "instructor"):
            self.assertIn(needed, ids)

    def test_sus_has_ten_items_and_interface_texts_match(self):
        self.assertEqual(len(I.SUS_ITEMS), 10)
        self.assertEqual(set(T["en"]), set(T["ar"]))


class Scoring(unittest.TestCase):
    def test_sus(self):
        best = {f"sus_{i}": (5 if i % 2 else 1) for i in range(1, 11)}
        worst = {f"sus_{i}": (1 if i % 2 else 5) for i in range(1, 11)}
        mid = {f"sus_{i}": 3 for i in range(1, 11)}
        self.assertEqual(S.sus_score(best), 100.0)
        self.assertEqual(S.sus_score(worst), 0.0)
        self.assertEqual(S.sus_score(mid), 50.0)
        self.assertIsNone(S.sus_score({}))
        self.assertIsNone(S.sus_score(dict(mid, sus_3=6)))           # out of range
        self.assertIsNone(S.sus_score(dict(mid, sus_3=True)))        # bool is not a rating
        # all fours: odd items give 3 each (15), even items give 1 each (5): 20 * 2.5 = 50
        self.assertEqual(S.sus_score({f"sus_{i}": 4 for i in range(1, 11)}), 50.0)

    def test_sus_known_value(self):
        # odd items 4 -> 3 each (x5 = 15), even items 2 -> 3 each (x5 = 15): (30) * 2.5 = 75
        ans = {f"sus_{i}": (4 if i % 2 else 2) for i in range(1, 11)}
        self.assertEqual(S.sus_score(ans), 75.0)

    def test_confidence_change_and_derived(self):
        pre = {i: 2 for i in I.CONFIDENCE_IDS}
        post = {i: 4 for i in I.CONFIDENCE_IDS}
        ch = S.confidence_change(pre, post)
        self.assertEqual(ch["mean"], 2.0)
        self.assertTrue(all(ch[i] == 2 for i in I.CONFIDENCE_IDS))
        self.assertIsNone(S.confidence_change(pre, {})["mean"])
        d = S.derived_metrics(sample_record(pre=pre, post=dict(post, **{f"sus_{i}": 3 for i in range(1, 11)})))
        self.assertEqual((d["confidence_pre_mean"], d["confidence_post_mean"], d["confidence_change_mean"]), (2.0, 4.0, 2.0))
        self.assertEqual((d["n_problems"], d["n_example_problems"], d["n_own_problems"]), (1, 1, 0))
        self.assertEqual(d["usage_minutes"], 10.0)
        self.assertEqual(d["sus"], 50.0)


class Storage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = ST.StudyStore(Path(self.tmp.name) / "study_data")

    def tearDown(self):
        self.tmp.cleanup()

    def test_ids(self):
        pid = ST.new_participant_id()
        self.assertRegex(pid, ST.ID_RE)
        self.assertNotEqual(pid, ST.new_participant_id())

    def test_save_load_and_files(self):
        rec = self.store.save(sample_record())
        pid = rec["participant_id"]
        self.assertTrue((self.store.dir / f"{pid}.json").exists())
        self.assertTrue((self.store.dir / f"{pid}.html").exists())
        self.assertEqual(self.store.load(pid)["participant"]["full_name"], "Ahmed Ali")
        self.assertIn("derived", self.store.load(pid))
        self.assertTrue((self.store.root / "master.csv").exists())
        self.assertTrue((self.store.root / "README.txt").exists())

    def test_report_contains_everything_the_researcher_needs(self):
        rec = self.store.save(sample_record())
        html = self.store.report_html(rec["participant_id"])
        for needle in ("Ahmed Ali", "Al-Nahrain University", "Operations Research", "Dr. X", "Linear programming",
                       "worked example 1", "max Z = 3*x1 + 5*x2", "Z = 36", "System Usability Scale", "Before", "After"):
            self.assertIn(needle, html, needle)

    def test_html_report_escapes_participant_text(self):
        rec = sample_record()
        rec["participant"]["full_name"] = "<script>alert(1)</script>"
        rec["post"]["comment"] = '"><img src=x onerror=alert(1)>'
        rec["problems"][0]["input"]["types"] = ["<="]
        html = ST.render_report_html(rec)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;script&gt;", html)

    def test_csv_formula_injection_is_neutralised(self):
        rec = sample_record()
        rec["participant"]["full_name"] = '=HYPERLINK("http://evil","x")'
        rec["participant"]["course"] = "@SUM(1+1)"
        row = ST.flat_row(rec)
        self.assertTrue(row["full_name"].startswith("'="))
        self.assertTrue(row["course"].startswith("'@"))
        text = ST.records_to_csv([rec])
        self.assertIn("participant_id", text.splitlines()[0])

    def test_master_csv_rows_and_delete(self):
        a = self.store.save(sample_record())
        b = self.store.save(sample_record(participant_id=ST.new_participant_id()))
        lines = (self.store.root / "master.csv").read_text(encoding="utf-8-sig").strip().splitlines()
        self.assertEqual(len(lines), 3)
        self.assertTrue(self.store.delete(a["participant_id"]))
        lines = (self.store.root / "master.csv").read_text(encoding="utf-8-sig").strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual([r["participant_id"] for r in self.store.records()], [b["participant_id"]])

    def test_path_traversal_is_impossible(self):
        for bad in ("../x", "OA-1", "", "OA-20260101-ZZZZZZ", "..\\x"):
            with self.assertRaises(ValueError):
                self.store.load(bad)
            with self.assertRaises(ValueError):
                self.store.delete(bad)

    def test_problem_summaries_for_all_kinds(self):
        cases = [
            dict(kind="transportation", input=dict(C=[[1, 2], [3, 4]], S=[5, 5], D=[4, 6]),
                 result=dict(dummy=None, start="vam", initial_costs={"vam": 20}, optimal_cost=20, modi_iterations=0,
                             status="optimal", degeneracy_repairs=0, alternative_optima=False, max_residual=0.0)),
            dict(kind="assignment", input=dict(C=[[1, 2], [3, 4]], maximize=False),
                 result=dict(assignment=[1, 2], total=5, padded=False, unassigned_columns=[])),
            dict(kind="nonlinear", input=dict(text="(x-2)**2", sign=1, a=0, b=5, tol=1e-6, x0=1, x1=2),
                 result=dict(methods=[dict(method="golden", status="converged", x=2.0, value=0.0, evaluations=30)],
                             bypassed=["newton"], grid_x=2.0, grid_value=0.0)),
        ]
        for p in cases:
            self.assertTrue(ST.problem_input_text(p) and ST.problem_result_text(p), p["kind"])

    def test_answer_text_does_not_repeat_the_number(self):
        items = {i.id: i for i in I.all_items(I.POST_SECTIONS)}
        self.assertEqual(ST.answer_text(items["overall_rating"], 4), "4 - Very good")
        self.assertEqual(ST.answer_text(items["recommend_nps"], 7), "7")
        self.assertEqual(ST.answer_text(items["sus_3"], 4), "4 – Agree")
        self.assertEqual(ST.answer_text(items["feat_examples"], 0), "0 – Did not use it")
        self.assertEqual(ST.answer_text(items["problems"], ["slow", "none"]), "It was slow; I met no problems")
        self.assertEqual(ST.answer_text(items["comment"], ""), "—")

    def test_participant_text_is_split_correctly(self):
        answers = {"consent_read": True, "full_name": "A B", "university": "U", "level": "y1", "standing": "good"}
        consent, participant, pre = ST.split_pre_answers(answers)
        self.assertEqual(consent, {"consent_read": True})
        self.assertEqual(participant, {"full_name": "A B", "university": "U", "level": "y1"})
        self.assertEqual(pre, {"standing": "good"})


class Email(unittest.TestCase):
    def settings(self, **kw):
        return StudySettings(smtp_host="smtp.example.org", smtp_user="u", smtp_password="p", smtp_to="r@example.org", **kw)

    def test_message_has_both_attachments(self):
        rec = sample_record()
        msg = ST.build_email(self.settings(), rec, "<html></html>")
        names = sorted(p.get_filename() for p in msg.iter_attachments())
        self.assertEqual(names, [f"{rec['participant_id']}.html", f"{rec['participant_id']}.json"])
        self.assertIn(rec["participant_id"], msg["Subject"])
        self.assertEqual(msg["To"], "r@example.org")

    def test_send_uses_starttls_login_and_send(self):
        with mock.patch("optiarchitect.study.storage.smtplib.SMTP") as smtp:
            ok, msg = ST.send_report(self.settings(), sample_record(), "<html></html>")
        self.assertEqual((ok, msg), (True, "sent"))
        inst = smtp.return_value.__enter__.return_value
        inst.starttls.assert_called_once()
        inst.login.assert_called_once_with("u", "p")
        inst.send_message.assert_called_once()

    def test_failure_never_raises(self):
        with mock.patch("optiarchitect.study.storage.smtplib.SMTP", side_effect=OSError("network down")):
            ok, msg = ST.send_report(self.settings(), sample_record(), "x")
        self.assertFalse(ok)
        self.assertIn("network down", msg)
        self.assertEqual(ST.send_report(StudySettings(), sample_record(), "x"), (False, "e-mail not configured"))


class Settings(unittest.TestCase):
    def test_environment_overrides(self):
        s = StudySettings.from_env({"OPTIARCHITECT_STUDY_DIR": "/tmp/x", "OPTIARCHITECT_MIN_PROBLEMS": "3",
                                    "OPTIARCHITECT_ETHICS_REF": "ABC-1", "OPTIARCHITECT_SMTP_HOST": "h",
                                    "OPTIARCHITECT_SMTP_PORT": "465", "OPTIARCHITECT_SMTP_SSL": "true"})
        self.assertEqual((str(s.data_dir), s.min_problems, s.ethics_ref, s.smtp_port, s.smtp_ssl),
                         ("/tmp/x", 3, "ABC-1", 465, True))
        self.assertTrue(s.email_enabled)
        self.assertEqual(StudySettings.from_env({"OPTIARCHITECT_MIN_PROBLEMS": "bad"}).min_problems, 1)


if __name__ == "__main__":
    unittest.main()
