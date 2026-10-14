"""
OptiArchitect Configuration
===========================
Global numerical settings, thresholds, and type definitions used across solvers.
"""

from typing import Optional, Callable, List, Tuple
import numpy as np

__version__ = "1.0.0"
AUTHOR = "Omar Ahmed Mohammed Al-Zuabidi"
COPYRIGHT = "(c) 2026 Omar Ahmed Mohammed Al-Zuabidi"
LICENSE = "MIT License"
REPOSITORY = "https://github.com/OmarAl-Zuabidi/OptiArchitect-Suite"

# --------------------------------------------------------------------------
# Numerical settings (single place, documented)
# --------------------------------------------------------------------------
EPS = 1e-9            # LP: pivot / sign tolerance
FEAS_TOL = 1e-7       # LP: Phase-I feasibility tolerance (scaled by problem size)
MAX_ITER = 10_000     # LP: hard iteration cap (reported as a status, never hidden)
BLAND_AFTER = 25      # LP: degenerate pivots before switching to Bland's rule
VALID_TYPES = ("<=", ">=", "=")
TOL = 1e-9            # Transportation / assignment: relative "zero" tolerance
SQRT_EPS = 1.5e-8     # NLP: ~sqrt(machine eps): best attainable x-accuracy
CURV_TOL = 1e-9       # NLP: |f''| below this is treated as zero curvature

TraceFn = Optional[Callable[[np.ndarray, List[int], List[str], str], None]]
Cell = Tuple[int, int]