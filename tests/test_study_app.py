"""End-to-end flow of the study application with a fake Streamlit session (no browser)."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from optiarchitect.study import instruments as I
from tests import fake_streamlit as fs


def answers_for(sections, prefix, **overrides):
    """A complete, valid set of widget values for the given sections."""
    out = {}
    for s in sections:
        for it in s.items:
            key = f"{prefix}_{it.id}"
            if it.kind == "text":
                out[key] = {"full_name": "Ahmed Test", "university": "Al-Nahrain University", "college": "Science",
                            "department": "Mathematics", "course": "Operations Research", "instructor": "Dr. Hassan"}[it.id]
            elif it.kind == "long_text":
                out[key] = "Very helpful tool."
            elif it.kind == "checkbox":
                out[key] = True
            elif it.kind == "single":
                out[key] = it.choices[0].value
            elif it.kind == "multi":
                out[key] = [it.choices[0].value]
            elif it.kind == "likert":
                out[key] = I.SCALES[it.scale][3][0]
    out.update({f"{prefix}_{k}": v for k, v in overrides.items()})
    return out


class StudyFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "study_data"
        self.env = mock.patch.dict(os.environ, {"OPTIARCHITECT_STUDY_DIR": str(self.dir)}, clear=False)
        self.env.start()
        for k in ("OPTIARCHITECT_SMTP_HOST", "OPTIARCHITECT_ADMIN_PASSWORD"):
            os.environ.pop(k, None)

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def files(self, ext):
        return sorted((self.dir / "participants").glob(f"*{ext}"))

    def test_first_screen_thanks_the_volunteer_and_shows_the_consent_information(self):
        s = fs.Session()
        s.run()
        self.assertIn("Thank you for volunteering", s.text)
        self.assertIn("Questionnaire before using the tool", s.text)
        self.assertIn("Confidentiality", s.text)
        self.assertEqual(s.state["study_stage"], "pre")
        self.assertEqual(self.files(".json"), [])

    def test_arabic_first_screen(self):
        s = fs.Session(state={"study_lang_value": "ar"})
        s.run()
        self.assertIn("شكرًا لتطوعك", s.text)
        self.assertIn("استمارة ما قبل استخدام الأداة", s.text)

    def test_incomplete_form_is_rejected_and_nothing_is_saved(self):
        s = fs.Session()
        s.run(pressed={"study_pre_form"})
        self.assertIn("Please complete all required questions", s.text)
        self.assertEqual(s.state["study_stage"], "pre")
        self.assertEqual(self.files(".json"), [])

    def test_consent_is_required(self):
        s = fs.Session(state=answers_for(I.PRE_SECTIONS, "pre", consent_data=False))
        s.run(pressed={"study_pre_form"})
        self.assertEqual(s.state["study_stage"], "pre")
        self.assertIn("agree that my answers", s.text)

    def test_full_session_produces_report_with_everything(self):
        s = fs.Session(state=answers_for(I.PRE_SECTIONS, "pre"))
        s.run(pressed={"study_pre_form"})
        self.assertEqual(s.state["study_stage"], "tool")
        saved = json.loads(self.files(".json")[0].read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "pre_completed")                 # checkpoint after questionnaire 1
        self.assertEqual(saved["participant"]["university"], "Al-Nahrain University")

        # the finish button is disabled until a problem was run
        s.run(set_state={"page": "part1"})
        self.assertIn("Problems run: **0**", s.text)
        s.run(pressed={"study_finish"})
        self.assertEqual(s.state["study_stage"], "tool")

        # run a worked example in the real OptiArchitect app inside the study
        s.run(set_state={"page": "part1", "mode_1": "ex", "ex_pick_1": 1}, pressed={"run_ex_1"})
        self.assertEqual(len(s.state["study_problems"]), 1)
        s.run(set_state={"page": "part3", "mode_3": "ex", "ex_pick_3": 2}, pressed={"run_ex_3"})
        s.run(set_state={"page": "part2", "mode_2": "ex", "ex_pick_2": 3}, pressed={"run_ex_2"})
        self.assertEqual(len(s.state["study_problems"]), 3)
        s.run()                                                              # re-render must not duplicate
        self.assertEqual(len(s.state["study_problems"]), 3)

        s.run(pressed={"study_finish"})
        self.assertEqual(s.state["study_stage"], "post")
        self.assertEqual(json.loads(self.files(".json")[0].read_text(encoding="utf-8"))["status"], "tool_completed")

        s.state.update(answers_for(I.POST_SECTIONS, "post"))
        s.run(pressed={"study_post_form"})
        self.assertEqual(s.state["study_stage"], "done")
        self.assertIn("Thank you - your answers were saved", s.text)

        rec = json.loads(self.files(".json")[0].read_text(encoding="utf-8"))
        self.assertEqual(rec["status"], "completed")
        self.assertEqual(rec["participant"]["full_name"], "Ahmed Test")
        self.assertTrue(rec["consent"]["consent_data"])
        self.assertEqual({p["kind"] for p in rec["problems"]}, {"lp", "nonlinear", "assignment"})
        lp = [p for p in rec["problems"] if p["kind"] == "lp"][0]
        self.assertEqual(lp["example"], 1)
        self.assertEqual(lp["result"]["status"], "optimal")
        self.assertAlmostEqual(lp["result"]["objective_value"], 36.0)
        self.assertIn("part1", rec["usage"]["pages"])
        self.assertTrue(rec["derived"]["sus"] is not None)
        self.assertIn("conf_formulate_lp", rec["pre"])
        self.assertIn("conf_formulate_lp", rec["post"])
        self.assertEqual(rec["derived"]["n_problems"], 3)

        html = self.files(".html")[0].read_text(encoding="utf-8")
        for needle in ("Ahmed Test", "Dr. Hassan", "Operations Research", "Linear programming", "worked example 1",
                       "Computed scores", "Mean change in confidence"):
            self.assertIn(needle, html)
        master = (self.dir / "master.csv").read_text(encoding="utf-8-sig")
        self.assertIn(rec["participant_id"], master)

    def test_own_problem_is_recorded_with_its_data(self):
        s = fs.Session(state=answers_for(I.PRE_SECTIONS, "pre"))
        s.run(pressed={"study_pre_form"})
        import pandas as pd
        xs = ["x1", "x2"]
        c = pd.DataFrame([[3.0, 5.0]], columns=xs, index=["Z"])
        k = pd.DataFrame([[1, 0, "<=", 4.0], [0, 2, "<=", 12.0], [3, 2, "<=", 18.0]], columns=xs + ["rel", "rhs"],
                         index=["C1", "C2", "C3"])
        s.run(set_state={"page": "part1", "mode_1": "own", "lp_n": 2, "lp_m": 3})
        fake_editors = {"lp_c_2": c, "lp_k_2_3": k}
        s.last.editors = fake_editors
        # the editors must be present in the run where the button is pressed
        orig = fs.Fake.__init__

        def init(self, *a, **kw):
            orig(self, *a, **kw)
            self.editors = fake_editors
        with mock.patch.object(fs.Fake, "__init__", init):
            s.run(pressed={"lp_go"})
        probs = list(s.state["study_problems"].values())
        self.assertEqual(len(probs), 1)
        self.assertIsNone(probs[0]["example"])
        self.assertEqual(probs[0]["input"]["b"], [4.0, 12.0, 18.0])
        self.assertAlmostEqual(probs[0]["result"]["objective_value"], 36.0)

    def test_withdrawal_deletes_the_data(self):
        s = fs.Session(state=answers_for(I.PRE_SECTIONS, "pre"))
        s.run(pressed={"study_pre_form"})
        self.assertEqual(len(self.files(".json")), 1)
        s.run(set_state={"study_withdraw_ok": True}, pressed={"study_withdraw"})
        self.assertEqual(s.state["study_stage"], "withdrawn")
        self.assertEqual(self.files(".json"), [])
        self.assertEqual(self.files(".html"), [])
        s.run()
        self.assertIn("You have withdrawn", s.text)

    def test_post_questionnaire_validation(self):
        s = fs.Session(state=answers_for(I.PRE_SECTIONS, "pre"))
        s.run(pressed={"study_pre_form"})
        s.run(set_state={"page": "part1", "mode_1": "ex", "ex_pick_1": 1}, pressed={"run_ex_1"})
        s.run(pressed={"study_finish"})
        post = answers_for(I.POST_SECTIONS, "post")
        post["post_sus_4"] = None                                   # one SUS item left blank
        s.state.update(post)
        s.run(pressed={"study_post_form"})
        self.assertEqual(s.state["study_stage"], "post")
        self.assertIn("I think that I would need the support", s.text)

    def test_exclusive_none_option(self):
        s = fs.Session(state=answers_for(I.PRE_SECTIONS, "pre", difficulties=["none", "time"]))
        s.run(pressed={"study_pre_form"})
        self.assertEqual(s.state["study_stage"], "pre")
        self.assertIn("on its own", s.text)

    def test_email_copy_is_attempted_when_configured(self):
        with mock.patch.dict(os.environ, {"OPTIARCHITECT_SMTP_HOST": "smtp.example.org",
                                          "OPTIARCHITECT_SMTP_TO": "r@example.org"}):
            with mock.patch("optiarchitect.study.storage.smtplib.SMTP") as smtp:
                s = fs.Session(state=answers_for(I.PRE_SECTIONS, "pre"))
                s.run(pressed={"study_pre_form"})
                s.run(set_state={"page": "part1", "mode_1": "ex", "ex_pick_1": 1}, pressed={"run_ex_1"})
                s.run(pressed={"study_finish"})
                s.state.update(answers_for(I.POST_SECTIONS, "post"))
                s.run(pressed={"study_post_form"})
        self.assertEqual(s.state["study_stage"], "done")
        smtp.return_value.__enter__.return_value.send_message.assert_called_once()
        rec = json.loads(self.files(".json")[0].read_text(encoding="utf-8"))
        self.assertEqual(rec["delivery"]["email"], "sent")

    def test_normal_app_is_unaffected_by_study_hooks(self):
        f = fs.run({"state": {"page": "part1", "mode_1": "ex", "ex_pick_1": 1}, "pressed": {"run_ex_1"}})
        self.assertIn("Completed - solution verified", "\n".join(f.out))
        self.assertNotIn("study_problems", f.session_state)


class Admin(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"OPTIARCHITECT_STUDY_DIR": str(Path(self.tmp.name) / "d")}, clear=False)
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_refuses_without_password(self):
        os.environ.pop("OPTIARCHITECT_ADMIN_PASSWORD", None)
        s = fs.Session(path=fs.ADMIN_PATH)
        s.run()
        self.assertIn("OPTIARCHITECT_ADMIN_PASSWORD", s.text)
        self.assertNotIn("<DATAFRAME>", s.text)

    def test_wrong_password_shows_nothing(self):
        with mock.patch.dict(os.environ, {"OPTIARCHITECT_ADMIN_PASSWORD": "correct horse"}):
            s = fs.Session(path=fs.ADMIN_PATH, state={"admin_pw": "wrong"})
            s.run()
        self.assertIn("Enter the password", s.text)
        self.assertNotIn("Participants (any status)", s.text)

    def test_correct_password_lists_participants(self):
        from optiarchitect.study import storage as ST
        from tests.test_study_core import sample_record
        ST.StudyStore(Path(self.tmp.name) / "d").save(sample_record())
        with mock.patch.dict(os.environ, {"OPTIARCHITECT_ADMIN_PASSWORD": "correct horse"}):
            s = fs.Session(path=fs.ADMIN_PATH, state={"admin_pw": "correct horse"})
            s.run()
        self.assertIn("Participants (any status)", s.text)
        self.assertIn("<DATAFRAME>", s.text)
        self.assertIn("<COMPONENT-HTML>", s.text)

    def test_password_check_is_exact(self):
        from optiarchitect.study.admin import authorised
        self.assertTrue(authorised("abc", "abc"))
        self.assertFalse(authorised("abd", "abc"))
        self.assertFalse(authorised("", ""))
        self.assertFalse(authorised("anything", ""))


if __name__ == "__main__":
    unittest.main()
