# Student study mode

OptiArchitect can run as a **research instrument** for a classroom or multi-university study. A student sees, in the
browser:

1. **Questionnaire 1** - a thank-you, the study information and consent, participant and course details (name,
   university, college, department, course, instructor), the student's situation in the subject, a 9-item
   self-rated confidence block, difficulties met, and expectations. Every answer is a choice.
2. **The tool** - the normal OptiArchitect web application. Every problem the student runs (a worked example or
   their own, with its data and result) is logged. A *Finish* button becomes available after a minimum number of problems.
3. **Questionnaire 2** - how the tool was used, the same 9 confidence items, the System Usability Scale (SUS),
   perceived-usefulness items, feature ratings, difficulties the tool helped with, an overall evaluation, problems met
   and one optional comment.
4. **A detailed report** for the researcher, saved inside the program folder (see "Where the data go").

The forms are available in **English and Arabic** (right-to-left layout).

## Quick start

```bash
pip install -e ".[web]"                 # Streamlit, pandas, SymPy, matplotlib
cd /path/where/study_data/should/live   # the data folder is created in the current directory
optiarchitect-study                     # participants' application  (opens http://localhost:8501)
```

The researcher's dashboard (password protected):

```bash
export OPTIARCHITECT_ADMIN_PASSWORD="a-long-passphrase"     # Windows: set OPTIARCHITECT_ADMIN_PASSWORD=...
optiarchitect-study-admin --server.port 8502
```

Without a password the dashboard refuses to start. It lists participants, shows descriptive statistics (and paired
tests if SciPy is installed), displays each report, and downloads `master.csv` or a ZIP of everything. It can also
delete a participant on request.

### Configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `OPTIARCHITECT_STUDY_DIR` | `study_data` | folder for the data (relative to where you start the program) |
| `OPTIARCHITECT_STUDY_TITLE`, `..._TITLE_AR` | evaluation of OptiArchitect | title shown to the student |
| `OPTIARCHITECT_RESEARCHER`, `OPTIARCHITECT_RESEARCHER_EMAIL`, `OPTIARCHITECT_INSTITUTION` | author's details | contact shown on the consent page - **set your own** |
| `OPTIARCHITECT_ETHICS_REF` | empty | ethics approval reference; shown only if set |
| `OPTIARCHITECT_MIN_PROBLEMS` | `1` | problems to run before the second questionnaire |
| `OPTIARCHITECT_ADMIN_PASSWORD` | empty | enables the dashboard |
| `OPTIARCHITECT_SMTP_HOST/PORT/USER/PASSWORD/FROM/TO/SSL` | empty | optional e-mail copy of each completed report (`..._SSL=true` for port 465, otherwise STARTTLS) |

## Where the data go

```
study_data/
  README.txt                    reminder about handling personal data
  master.csv                    one row per participant (UTF-8 with BOM, opens in Excel)
  participants/OA-20261012-3fa9c1.json   complete record (machine-readable)
  participants/OA-20261012-3fa9c1.html   the readable report: open it in any browser
```

* A questionnaire is saved when it is submitted: after questionnaire 1 (`status: pre_completed`), when the student
  finishes the tool (`tool_completed`) and after questionnaire 2 (`completed`). If a student leaves in the middle,
  the earlier part is still there.
* The report contains: participant and institution data, consent, all answers before and after, every problem
  with its input data and the result (method, status, objective value, solution, verification figure), pages and
  features used, the time spent, SUS, mean confidence before/after and the change, usefulness.
* `master.csv` has one column per question (`pre_...`, `post_...`) plus the scores, so it can go straight into
  SPSS, R, Python or Excel. Free-text cells beginning with `=`, `+`, `-` or `@` are prefixed so that a spreadsheet
  cannot run them as formulas.
* The folder `study_data/` is listed in `.gitignore`. **Never publish it**: it contains personal data.

### Hosting and data safety

| Option | Notes |
|---|---|
| Your laptop or a lab PC (`optiarchitect-study`) | simplest; students on the same network open `http://<your-ip>:8501` (start with `--server.address 0.0.0.0`); data stay on your machine |
| A university or own server | best for several sessions; use HTTPS, restrict the folder permissions, back it up |
| Free cloud hosts (e.g. Streamlit Community Cloud) | the disk is usually **temporary**, so reports can disappear when the app restarts. Use the e-mail copy and download the data often; check where the host stores data and whether this is acceptable for personal data |

## The questionnaires

| Block | When | Items | Basis |
|---|---|---|---|
| Consent | before | 4 required statements | study information on the same page |
| Participant and course | before | 7 | requested fields |
| Situation, tools, device, preferred language | before | 8 | developer-written, closed choices |
| **Confidence** (9 tasks, 1-5) | before **and** after | 9 | developer-written; identical wording so the change can be computed per student |
| Difficulties and expectations | before | 4 | developer-written |
| **System Usability Scale** | after | 10 | Brooke (1996); score 0-100 |
| **Perceived usefulness** | after | 8 | adapted from the Technology Acceptance Model, Davis (1989) |
| How the tool was used | after | 1 | developer-written |
| Features, impact, overall, problems | after | 16 | developer-written; one optional free-text comment |

### Limits you should state in your own paper

* SUS is a validated English instrument; the **Arabic wording is a working translation by the developer and has not been
  psychometrically validated**. Use a validated Arabic version if you can find one, or report the limitation.
* The confidence items and the usefulness items are **not validated scales**; the usefulness items are adapted in
  spirit from TAM, not copied. Treat results as exploratory and pilot the forms with a few students first.
* All answers are self-reported. A single-group before/after design cannot show that the tool *caused* a change
  (no control group; practice and familiarity also matter).
* About 68 is the commonly cited average SUS score (Sauro, 2011); it is a benchmark, not a pass mark.
* For the paired comparison of confidence use a paired t-test or Wilcoxon signed-rank test, report the effect size
  and the number of completed pairs, and say how you handled students who did not finish.

## Ethics and privacy checklist (not legal advice)

1. Get the approval or permission your institution requires for research with students **before** the first session.
   Put the reference in `OPTIARCHITECT_ETHICS_REF`.
2. Make sure every statement on the consent page is true for your study. In particular the page says that data are
   not shared with the student's instructor or university and that participation is voluntary; honour that, and do not
   make participation part of any grade.
3. Replace the default contact details with your own.
4. Collect only what you need. The names are needed for the study design you chose; consider removing the name and
   the instructor's name from the exported data before sharing or analysing it.
5. Store the folder on an encrypted, access-controlled disk; keep a back-up; set a retention date and delete the data after it.
6. Delete a participant on request (dashboard, or delete the `.json` and `.html` files and rebuild `master.csv`).
7. Report results in aggregate. Do not publish names, universities or instructors in a way that identifies anyone.
8. Follow the data-protection rules that apply to you.

## Before the first real session

* **Pilot** the forms with 3 to 5 students (including on a phone) and fix whatever confuses them.
* The consent page says the study takes "about 15 to 20 minutes". That is an **estimate**: time your pilot and
  edit `texts.py` accordingly.
* Have an Arabic-speaking colleague read the Arabic questions and the consent text; the translation was not reviewed
  by a second person.
* Run one complete test session yourself and open the report in `study_data/`.

## Changing the study

* Questions are plain data in `src/optiarchitect/study/instruments.py`. Keep the `id` of an item stable once data have been
  collected, give every text in both languages, and run the tests (`python -m unittest discover -s tests -t .`);
  they check that both languages are complete and that scoring still works.
* The consent text is in `src/optiarchitect/study/texts.py`.
* `StudySettings.min_problems` controls when *Finish* becomes available.

## References

* Brooke, J. (1996). SUS: a "quick and dirty" usability scale. In P. W. Jordan et al. (Eds.), *Usability Evaluation in
  Industry* (pp. 189-194). London: Taylor & Francis.
* Davis, F. D. (1989). Perceived usefulness, perceived ease of use, and user acceptance of information technology.
  *MIS Quarterly*, 13(3), 319-340. https://doi.org/10.2307/249008
* Sauro, J. (2011). *A Practical Guide to the System Usability Scale*. Denver: Measuring Usability LLC.
