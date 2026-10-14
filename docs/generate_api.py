"""Generate docs/api.md from the real signatures and docstrings, so the API reference cannot drift.

    python docs/generate_api.py            # rewrite docs/api.md
    python docs/generate_api.py --check    # exit 1 if docs/api.md is out of date (used by the tests)
"""
import dataclasses
import inspect
import pathlib
import sys

from optiarchitect.core import assignment, lp, nlp, transportation
from optiarchitect.utils import parser

SECTIONS = [
    ("Linear programming (`optiarchitect.core.lp`)", lp,
     ["solve_lp", "choose_method", "lp_applicability", "max_violation", "LPResult"]),
    ("Transportation (`optiarchitect.core.transportation`)", transportation,
     ["solve_transportation", "northwest_corner", "least_cost", "vogel", "complete_basis", "modi_optimize",
      "TransportResult", "TransportSolution", "IBFS", "Step", "MODIIteration"]),
    ("Assignment (`optiarchitect.core.assignment`)", assignment, ["hungarian", "AssignResult", "AssignStep"]),
    ("Non-linear optimization (`optiarchitect.core.nlp`)", nlp,
     ["run_method", "diagnose", "golden_section", "fibonacci_search", "bisection_search", "newton_raphson",
      "secant_method", "check_unimodality", "check_unimodality_detail", "grid_minimum", "OptResult"]),
    ("Safe formulas (`optiarchitect.utils.parser`)", parser, ["Objective", "EvalError"]),
]


def render() -> str:
    out = ["# API reference", "",
           "Generated from the docstrings by `docs/generate_api.py`; do not edit by hand.",
           "All solvers are pure functions: they never print and return the dataclasses listed here.", ""]
    for title, mod, names in SECTIONS:
        out += [f"## {title}", ""]
        for name in names:
            obj = getattr(mod, name)
            if inspect.isclass(obj):
                if dataclasses.is_dataclass(obj):
                    fields = ", ".join(f.name for f in dataclasses.fields(obj))
                    head = f"class {name}({fields})"
                else:
                    head = f"class {name}{inspect.signature(obj)}" if name != "EvalError" else f"class {name}(Exception)"
            else:
                head = f"{name}{inspect.signature(obj)}"
            out += [f"### `{name}`", "", "```python", head, "```", "", inspect.getdoc(obj) or "*(no description)*", ""]
    return "\n".join(out).rstrip() + "\n"


if __name__ == "__main__":
    target = pathlib.Path(__file__).with_name("api.md")
    text = render()
    if "--check" in sys.argv:
        sys.exit(0 if target.exists() and target.read_text(encoding="utf-8") == text else 1)
    target.write_text(text, encoding="utf-8")
    print("wrote", target)
