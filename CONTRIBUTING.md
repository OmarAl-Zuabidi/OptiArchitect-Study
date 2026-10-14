# Contributing to OptiArchitect

Thank you for your interest. Bug reports, documentation fixes and new teaching examples are welcome.

## Set up

```bash
git clone https://github.com/OmarAl-Zuabidi/OptiArchitect-Suite.git
cd OptiArchitect-Suite
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[all]"
```

## Before opening a pull request

```bash
python -m unittest discover -s tests -t . -v      # all tests must pass
optiarchitect --selftest                          # 15/15 checks
```

- Solvers in `src/optiarchitect/core/` must stay **pure** (no `input()` or `print()`); they return dataclasses.
- Every user-visible sentence belongs in `src/optiarchitect/messages.py` **in both languages** with the same
  placeholders (the self-test enforces this).
- Never evaluate user formulas with `eval`; use `optiarchitect.utils.parser.Objective`.
- A change to a numerical method should come with a test, and, when relevant, a re-run of
  `python validation/run_validation.py` (requires `pip install ".[validation]"`).

## Reporting a problem

Open an issue and include the command or code you ran, the full output, your Python version and OS.
For a wrong result, please include the problem data so that it can be reproduced.

## Getting help

Open an issue with the label `question` and include your Python version, operating system, the command or code
you ran and the full output. We aim to answer within a few days; this is a volunteer-maintained project.

## Documentation changes

`docs/api.md` is generated from the docstrings: after editing a docstring run `python docs/generate_api.py`
(a test fails if it is out of date). Keep the examples in `examples/` runnable; a test runs them.
