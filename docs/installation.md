# Installation

Requires **Python 3.10 or newer**. The core needs only NumPy; everything else is an optional extra.

```bash
git clone https://github.com/OmarAl-Zuabidi/OptiArchitect-Suite.git
cd OptiArchitect-Suite
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[all]"                                   # development install with every extra
```

| Extra | Adds | Needed for |
|---|---|---|
| `nlp` | sympy | Part 3 (formula parsing and derivatives) |
| `plot` | matplotlib | graphical method, f(x) plot |
| `arabic` | arabic-reshaper, python-bidi | correct Arabic shaping in consoles and plots |
| `web` | streamlit, pandas, sympy, matplotlib | browser interface |
| `validation` | scipy | `validation/run_validation.py` |
| `all` | all of the above | |

A minimal install is `pip install .` (NumPy only: Parts 1 and 2 work; Part 3 asks for the `nlp` extra).

## Check the installation

```bash
optiarchitect --version
optiarchitect --selftest           # 15 checks, expected: "Self-test: 15/15 checks passed."
python -m unittest discover -s tests -t . -v      # 62 automated tests
python examples/01_linear_programming.py          # runs without any input
```

## Troubleshooting

* *Arabic text looks disconnected in a console or plot*: install the `arabic` extra and run `optiarchitect --shape-ar`.
* *Part 3 says SymPy is missing*: `pip install ".[nlp]"`.
* *Plots do not open on a server*: set `MPLBACKEND=Agg` (the web interface does this itself).
