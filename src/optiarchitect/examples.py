"""
OptiArchitect worked examples (identical to the reference program).
Shared by the web app, the CLI and the self-test.
"""

LP_EXAMPLES = {
    1: dict(c=[3, 5], A=[[1, 0], [0, 2], [3, 2]], b=[4, 12, 18], types=["<=", "<=", "<="], obj="max"),
    2: dict(c=[2, 3], A=[[1, 1], [1, 3]], b=[4, 6], types=[">=", ">="], obj="min"),
    3: dict(c=[3, 2], A=[[1, 1], [1, 0]], b=[4, 3], types=["=", "<="], obj="max"),
}

TP_EXAMPLES = {
    1: dict(C=[[9, 4, 2, 2], [11, 9, 9, 5], [9, 14, 11, 14]], S=[40, 30, 40], D=[15, 5, 45, 45]),
    2: dict(C=[[4, 6, 8, 5], [7, 3, 5, 6], [6, 8, 4, 7]], S=[20, 30, 25], D=[10, 25, 15, 10]),
}

AS_EXAMPLES = {
    3: dict(C=[[9, 2, 7, 8], [6, 4, 3, 7], [5, 8, 1, 8], [7, 6, 9, 4]], maximize=False),
    4: dict(C=[[10, 12, 9, 14], [8, 15, 11, 9], [13, 9, 12, 10]], maximize=True),
}

NL_EXAMPLES = {
    1: dict(text="(x-2)**2+1", sign=1, a=0.0, b=5.0, tol=1e-6, x0=2.5, x1=3.0),
    2: dict(text="x*exp(-x)", sign=-1, a=0.0, b=5.0, tol=1e-6, x0=0.5, x1=0.8),
    3: dict(text="x**4-3*x**3+2", sign=1, a=0.0, b=3.0, tol=1e-6, x0=1.5, x1=2.0),
}

# part -> (example numbers shown in that part)
EXAMPLE_RANGE = {1: (1, 2, 3), 2: (1, 2, 3, 4), 3: (1, 2, 3)}
