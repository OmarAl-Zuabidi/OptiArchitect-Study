"""
OptiArchitect Core Module
========================
Central exports for optimization algorithms, data structures, and utilities.
"""

# 1. Linear Programming & Simplex (lp.py)
from .lp import (
    LPResult,
    solve_lp,
    choose_method,
    max_violation,
)

# 2. Nonlinear Optimization (nlp.py)
from .nlp import (
    OptResult,
    golden_section,
    fibonacci_search,
    bisection_search,
    newton_raphson,
    secant_method,
    check_unimodality_detail,
    check_unimodality,
    grid_minimum,
    diagnose,
    run_method,
)

# 3. Transportation Problems (transportation.py)
from .transportation import (
    Step,
    IBFS,
    MODIIteration,
    TransportSolution,
    TransportResult,
    northwest_corner,
    least_cost,
    vogel,
    complete_basis,
    modi_optimize,
    solve_transportation,
)

# 4. Assignment Problems (assignment.py)
from .assignment import (
    AssignStep,
    AssignResult,
    hungarian,
)


__all__ = [
    # LP
    "LPResult",
    "solve_lp",
    "choose_method",
    "max_violation",
    # NLP
    "OptResult",
    "golden_section",
    "fibonacci_search",
    "bisection_search",
    "newton_raphson",
    "secant_method",
    "check_unimodality_detail",
    "check_unimodality",
    "grid_minimum",
    "diagnose",
    "run_method",
    # Transportation
    "Step",
    "IBFS",
    "MODIIteration",
    "TransportSolution",
    "TransportResult",
    "northwest_corner",
    "least_cost",
    "vogel",
    "complete_basis",
    "modi_optimize",
    "solve_transportation",
    # Assignment
    "AssignStep",
    "AssignResult",
    "hungarian",
]