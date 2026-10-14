# Changelog

All notable changes are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/),
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **Student study mode** (`optiarchitect-study`, `optiarchitect-study-admin`): bilingual pre-use and post-use
  questionnaires (consent, profile, confidence, System Usability Scale, perceived usefulness ...), logging of the
  problems a student solves, a detailed per-participant report (HTML + JSON + `master.csv`) saved in `study_data/`,
  optional e-mail copy and a password-protected researcher dashboard. See `docs/study.md`.
- `docs/` (installation, usage, methods, generated API reference), `examples/` (three runnable scripts) and tests for
  the examples, the documentation and the study mode.
- Docstrings for every public function and result class.

### Changed
- `app.py` no longer runs at import time and takes `main(configure_page=True)`; `streamlit run app.py` is unchanged.

## [1.0.0] - 2026-10-07

First public release.

### Added
- Part 1 - linear programming: standard, dual and two-phase simplex with an applicability report,
  Bland's rule fallback, independent constraint check and a graphical method for two variables.
- Part 2 - transportation (North-West Corner, Least Cost, Vogel, MODI with degeneracy repair) and
  assignment (Hungarian method, rectangular and maximisation cases).
- Part 3 - single-variable non-linear optimization: Golden Section, Fibonacci, Newton-Raphson and secant,
  with white-listed formula parsing, symbolic derivatives and method diagnosis.
- Interactive bilingual (English / Arabic) console (`optiarchitect`), Streamlit web application
  (`optiarchitect-web`) and Python API.
- Built-in 15-check self-test, 19 automated tests and a reproducible validation study against SciPy
  (`validation/run_validation.py`).
