"""
OptiArchitect - an interactive, bilingual (English / Arabic) teaching toolkit for
Operations Research and optimization.

    from optiarchitect import solve_lp, solve_transportation, hungarian, Objective

Part 1  Linear Programming ........ Standard / Dual / Two-Phase Simplex, graphical method
Part 2  Transportation & Assignment  NWC, Least Cost, Vogel, MODI, Hungarian
Part 3  Single-variable NLP ....... Golden Section, Fibonacci, Newton-Raphson, Secant

Interfaces:  ``optiarchitect`` (console)  |  ``optiarchitect-web`` (browser)
"""
from optiarchitect.config import AUTHOR, COPYRIGHT, LICENSE, __version__
from optiarchitect.core import *          # noqa: F401,F403  (solvers and result types)
from optiarchitect.core import __all__ as _core_all
from optiarchitect.utils.parser import EvalError, Objective

__all__ = ["__version__", "AUTHOR", "COPYRIGHT", "LICENSE", "EvalError", "Objective", *_core_all]
