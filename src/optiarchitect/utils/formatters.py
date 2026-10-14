"""
OptiArchitect Formatting & Export Utilities
==========================================
Functions to format tableaux, matrices, and optimization solutions 
into Plain Text, Markdown, and LaTeX formats.
"""

from typing import List, Optional
import numpy as np


def format_matrix_text(matrix: np.ndarray, row_labels: Optional[List[str]] = None, col_labels: Optional[List[str]] = None, precision: int = 2) -> str:
    """Formats a 2D numpy array into a clean ASCII table."""
    m, n = matrix.shape
    r_labels = row_labels if row_labels else [f"R{i+1}" for i in range(m)]
    c_labels = col_labels if col_labels else [f"C{j+1}" for j in range(n)]

    col_widths = [max(len(cl), 8) for cl in c_labels]
    row_label_width = max(len(rl) for rl in r_labels) + 2

    header = " " * row_label_width + " | " + " | ".join(f"{cl:^{w}}" for cl, w in zip(c_labels, col_widths))
    divider = "-" * len(header)

    lines = [header, divider]
    for i in range(m):
        row_str = f"{r_labels[i]:<{row_label_width}} | "
        vals = []
        for j in range(n):
            val = matrix[i, j]
            vals.append(f"{val:^{col_widths[j]}.{precision}f}")
        row_str += " | ".join(vals)
        lines.append(row_str)

    return "\n".join(lines)


def format_tableau_markdown(tableau: np.ndarray, basic_vars: List[str], var_names: List[str]) -> str:
    """Formats a Simplex Tableau into a Markdown Table."""
    m, n = tableau.shape
    headers = ["Basis"] + var_names + ["RHS"]
    
    header_line = "| " + " | ".join(headers) + " |"
    divider_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    
    rows = [header_line, divider_line]
    for i in range(m - 1):
        row_vals = [f"{v:.2f}" for v in tableau[i]]
        b_var = basic_vars[i] if i < len(basic_vars) else f"x{i}"
        rows.append(f"| {b_var} | " + " | ".join(row_vals) + " |")

    # Objective Row (Last Row)
    obj_vals = [f"{v:.2f}" for v in tableau[-1]]
    rows.append("| z | " + " | ".join(obj_vals) + " |")

    return "\n".join(rows)


def format_matrix_latex(matrix: np.ndarray, environment: str = "bmatrix", precision: int = 2) -> str:
    """Formats a 2D numpy array into a LaTeX matrix string."""
    m, n = matrix.shape
    lines = [f"\\begin{{{environment}}}"]
    for i in range(m):
        row_str = " & ".join(f"{matrix[i, j]:.{precision}f}" for j in range(n)) + " \\\\"
        lines.append("  " + row_str)
    lines.append(f"\\end{{{environment}}}")
    return "\n".join(lines)


def export_solution_summary(result_obj) -> str:
    """Human-readable text summary for LPResult, TransportResult, AssignResult or OptResult."""
    lines = ["=" * 60, "               OPTIARCHITECT SOLUTION SUMMARY", "=" * 60]

    sol = getattr(result_obj, "solution", None)          # TransportResult wraps a TransportSolution
    status = getattr(result_obj, "status", None) or getattr(sol, "status", None)
    if status is not None:
        lines.append(f"Status:          {status}")
    if getattr(result_obj, "z", None) is not None:       # LPResult
        lines.append(f"Objective Value: {result_obj.z:.4f}")
    if getattr(result_obj, "fx", None) is not None:      # OptResult
        lines.append(f"f(x*):           {result_obj.fx:.6g}")
    cost = getattr(result_obj, "cost", None)
    if cost is None and sol is not None:
        cost = sol.cost
    if cost is not None:
        lines.append(f"Cost/Value:      {cost:.4f}")
    x = getattr(result_obj, "x", None)
    if x is not None:
        lines.append(f"Solution Vector: {np.round(x, 4)}")
    lines.append("=" * 60)
    return "\n".join(lines)
