# OptiArchitect

[![CI](https://github.com/OmarAl-Zuabidi/OptiArchitect-Suite/actions/workflows/ci.yml/badge.svg)](https://github.com/OmarAl-Zuabidi/OptiArchitect-Suite/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.txt)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)

OptiArchitect is a Python toolkit that implements the classical operations research algorithms as small,
**observable** functions and **verifies every result independently**. It has an English/Arabic console, a
Streamlit web application and a Python API, all on one solver core.

## Statement of need

Production solvers (HiGHS through SciPy, Pyomo, CVXPY, spreadsheet solvers) are fast and correct but hide the
algorithmic path; scripts written for teaching show the path but are rarely tested on degenerate, infeasible,
unbounded, unbalanced or rectangular cases. People who study how OR algorithms behave, or how OR is learned, need
reference implementations whose internal states are observable and whose correctness is demonstrated. OptiArchitect
provides:

* **Observable algorithms** - a trace callback delivers every tableau, MODI loop or iteration as data;
* **Explained applicability** - the program recommends a method and says why the others are bypassed;
* **Independent verification** - constraint residuals, supply-demand residuals or a grid scan for every answer;
* **Arabic and English** - complete interface text and right-to-left handling.

Intended users: OR instructors and education researchers, researchers who need observable reference
implementations, and developers of teaching software.

| Part | Topic | Methods |
|---|---|---|
| 1 | Linear programming | Standard, dual and two-phase simplex; graphical method (2 variables) |
| 2 | Transportation and assignment | North-West Corner, Least Cost, Vogel (VAM), MODI (u-v), Hungarian |
| 3 | Single-variable non-linear optimization | Golden Section, Fibonacci, Newton-Raphson, secant (automatic derivatives) |

## Installation

Requires Python 3.10 or newer. Full details and troubleshooting: [docs/installation.md](docs/installation.md).

```bash
git clone https://github.com/OmarAl-Zuabidi/OptiArchitect-Suite.git
cd OptiArchitect-Suite
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[all]"                                 # core needs only NumPy; extras: nlp, plot, arabic, web, validation
optiarchitect --selftest                                # expected: "Self-test: 15/15 checks passed."
```

## Example usage

```python
from optiarchitect import solve_lp, solve_transportation, hungarian, Objective
from optiarchitect.core import run_method

res = solve_lp([3, 5], [[1, 0], [0, 2], [3, 2]], [4, 12, 18], ["<="] * 3, "max")
print(res.method, res.status, res.z, res.x)           # standard optimal 36.0 [2. 6.]

tp = solve_transportation([[4, 6, 8, 5], [7, 3, 5, 6], [6, 8, 4, 7]], [20, 30, 25], [10, 25, 15, 10])
print(tp.dummy, tp.start, tp.solution.cost)           # destination vam 225.0

obj = Objective("x*exp(-x)", sign=-1)                 # maximise; formula is validated, never eval'ed
print(run_method(obj, "newton", 0, 5, 0.5, 0.8, 1e-8).x)   # 1.0 (to 8 digits)
```

Interactive use:

```bash
optiarchitect                    # console (also: python -m optiarchitect)
optiarchitect --lang ar --part 2 # Arabic, open Part 2 directly
optiarchitect --detail           # show every tableau / MODI loop / iteration
optiarchitect-web                # browser interface
optiarchitect-study              # student-study application (questionnaires + tool + report)
```

Three complete, runnable scripts with their output are in [examples/](examples).

## Student study mode

The same program can be run as a **classroom research instrument**: the student sees a pre-use questionnaire
(thanks, consent, name, university, college, department, course, instructor, situation in the subject, confidence,
difficulties), then the tool, then a post-use questionnaire (System Usability Scale, usefulness, features, overall
evaluation). Every problem the student runs is logged and a detailed report is saved in `study_data/` for the
researcher. Forms are in English and Arabic.

```bash
pip install -e ".[web]"
optiarchitect-study                                        # participants
OPTIARCHITECT_ADMIN_PASSWORD="..." optiarchitect-study-admin   # researcher dashboard
```

Read [docs/study.md](docs/study.md) first: data layout, hosting, the questionnaires and their limits, and the ethics
checklist. `study_data/` holds personal data and is excluded from git.

## Documentation

* [docs/usage.md](docs/usage.md) - console, web application and API, with real output
* [docs/study.md](docs/study.md) - student study mode: questionnaires, reports, ethics checklist
* [docs/methods.md](docs/methods.md) - algorithms, routing and diagnosis rules, verification checks
* [docs/api.md](docs/api.md) - API reference generated from the docstrings
* [validation/](validation) - reproducible comparison with SciPy

## Tests

```bash
python -m unittest discover -s tests -t . -v      # 62 automated tests
python validation/run_validation.py               # 1000 LPs, 500 transportation, 1000 assignment, 8 NLP cases
```

Results of the validation study for release 1.0.0 are in `validation/results.json`.

## Limitations

Dense tableaux for teaching-size and benchmark-size models (not large sparse problems), one-variable
non-linear problems only, and no integer programming.

## Community guidelines

* **Contribute:** see [CONTRIBUTING.md](CONTRIBUTING.md) (set-up, tests required for a pull request, coding rules).
* **Report a problem or request a feature:** open an issue at
  <https://github.com/OmarAl-Zuabidi/OptiArchitect-Suite/issues> using the templates provided.
* **Get help:** open an issue with the label `question`; include your Python version, the command or code you ran
  and the full output. Security problems: see [SECURITY.md](SECURITY.md).
* Please follow the [code of conduct](CODE_OF_CONDUCT.md). Release notes: [CHANGELOG.md](CHANGELOG.md).

## Citation

Please cite the software using [CITATION.cff](CITATION.cff) (GitHub offers "Cite this repository"):

> Al-Zuabidi, O. A. M. (2026). *OptiArchitect* (Version 1.0.0) [Computer software].
> https://github.com/OmarAl-Zuabidi/OptiArchitect-Suite

## Licence

MIT - see [LICENSE.txt](LICENSE.txt). Copyright (c) 2026 Omar Ahmed Mohammed Al-Zuabidi.
