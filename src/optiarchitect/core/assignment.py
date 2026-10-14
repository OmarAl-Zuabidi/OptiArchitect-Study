from dataclasses import dataclass
from typing import List, Optional, Set
import numpy as np

from optiarchitect.config import TOL


# ==========================================================================
#                         ASSIGNMENT: HUNGARIAN
# ==========================================================================

@dataclass
class AssignStep:
    """One state of the Hungarian method (``kind`` ``"row"``, ``"col"``, ``"adjust"`` or ``"done"``)
    with the reduced ``matrix``, the size of the zero matching and the adjustment ``delta``.
    """
    kind: str                   # 'row' | 'col' | 'adjust' | 'done'
    matrix: np.ndarray
    matched: int = 0
    delta: float = 0.0


@dataclass
class AssignResult:
    """Result of :func:`hungarian`.

    ``assignment[i]`` is the column given to original row ``i`` (``None`` if the row got a dummy);
    ``unassigned_cols`` lists real columns left without a row; ``cost`` is measured in the
    *original* matrix; ``steps`` records the method; ``padded`` is ``True`` for rectangular input.
    """
    assignment: List[Optional[int]]   # per original row: column index or None (dummy)
    unassigned_cols: List[int]        # real columns left without a row
    cost: float                       # in the ORIGINAL cost matrix
    steps: List[AssignStep]
    padded: bool


def _max_zero_matching(Z: np.ndarray):
    n = Z.shape[0]
    match_col = [-1] * n

    def try_row(i, seen):
        for j in range(n):
            if Z[i, j] and not seen[j]:
                seen[j] = True
                if match_col[j] == -1 or try_row(match_col[j], seen):
                    match_col[j] = i
                    return True
        return False

    size = sum(try_row(i, [False] * n) for i in range(n))
    return size, match_col


def hungarian(C, maximize: bool = False) -> AssignResult:
    """Hungarian algorithm for the assignment problem (row/column reduction + minimum line cover).

    Args:
        C: cost (or profit) matrix, 2-D, finite, any shape; a rectangular matrix is padded with
            dummy rows or columns.
        maximize: treat ``C`` as profits to be maximised.

    Returns:
        :class:`AssignResult`; its ``cost`` is the total in the original matrix.

    Raises:
        ValueError: for an empty, non-2-D or non-finite matrix.
    """
    C0 = np.asarray(C, dtype=float)
    if C0.ndim != 2 or min(C0.shape) < 1:
        raise ValueError("Cost matrix must be 2-D and non-empty")
    if not np.isfinite(C0).all():
        raise ValueError("Costs must be finite numbers (no NaN/Inf)")
    
    r0, c0 = C0.shape
    n = max(r0, c0)
    W = (C0.max() - C0) if maximize else C0.copy()
    P = np.zeros((n, n))
    P[:r0, :c0] = W
    steps: List[AssignStep] = []
    scale = max(1.0, float(np.abs(P).max()))
    tol = TOL * scale

    # Step 1: Row Reduction
    P = P - P.min(axis=1, keepdims=True)
    steps.append(AssignStep("row", P.copy()))

    # Step 2: Column Reduction
    P = P - P.min(axis=0, keepdims=True)
    P[np.abs(P) < tol] = 0.0
    steps.append(AssignStep("col", P.copy()))

    # Step 3 & 4: Maximum Matching & Matrix Adjustments
    for _ in range(n * n + 5):
        size, match_col = _max_zero_matching(P <= tol)
        if size == n:
            steps.append(AssignStep("done", P.copy(), size))
            break

        match_row = [-1] * n
        for j, i in enumerate(match_col):
            if i >= 0:
                match_row[i] = j

        mrows = {i for i in range(n) if match_row[i] == -1}       # Kőnig: marked rows
        mcols: Set[int] = set()
        changed = True

        while changed:
            changed = False
            for i in list(mrows):
                for j in range(n):
                    if P[i, j] <= tol and j not in mcols:
                        mcols.add(j)
                        changed = True
                        if match_col[j] != -1 and match_col[j] not in mrows:
                            mrows.add(match_col[j])

        ur = sorted(mrows)                                         # uncovered rows
        uc = [j for j in range(n) if j not in mcols]               # uncovered cols
        d = float(P[np.ix_(ur, uc)].min())
        covered_r = [i for i in range(n) if i not in mrows]

        P[np.ix_(ur, uc)] -= d
        P[np.ix_(covered_r, sorted(mcols))] += d
        P[np.abs(P) < tol] = 0.0
        steps.append(AssignStep("adjust", P.copy(), size, d))
    else:
        raise RuntimeError("Hungarian algorithm did not converge")

    assignment: List[Optional[int]] = [None] * r0
    taken = set()
    for j, i in enumerate(match_col):
        if i < r0 and j < c0:
            assignment[i] = j
            taken.add(j)

    cost = float(sum(C0[i, j] for i, j in enumerate(assignment) if j is not None))
    return AssignResult(assignment, [j for j in range(c0) if j not in taken], cost, steps, r0 != c0)