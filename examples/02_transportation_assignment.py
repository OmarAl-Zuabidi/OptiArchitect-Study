"""Transportation (starting rules + MODI, dummy destination) and the Hungarian method.

Run:  python examples/02_transportation_assignment.py
"""

from optiarchitect import hungarian, solve_transportation

# 3 sources (supply 75) and 4 destinations (demand 60): a zero-cost dummy destination absorbs 15 units.
C = [[4, 6, 8, 5], [7, 3, 5, 6], [6, 8, 4, 7]]
supply, demand = [20, 30, 25], [10, 25, 15, 10]

res = solve_transportation(C, supply, demand)                              # start="best"
print("dummy added            :", res.dummy)
print("initial costs          :", {k: v.cost for k, v in res.ibfs.items()})
print("starting method used   :", res.start)
print("MODI iterations        :", len(res.solution.iterations))
print("optimal cost           :", res.solution.cost, "(status:", res.solution.status + ")")
print("independent residual   :", res.max_residual)
print("optimal plan (last column = dummy destination):")
print(res.solution.X.astype(int))

# Assignment, rectangular and maximising: 3 workers, 4 jobs (a dummy row is added automatically).
profit = [[10, 12, 9, 14], [8, 15, 11, 9], [13, 9, 12, 10]]
a = hungarian(profit, maximize=True)
print("\nHungarian (maximise, padded =", a.padded, ")")
print("assignment (row -> column):", {i + 1: (None if j is None else j + 1) for i, j in enumerate(a.assignment)})
print("unassigned columns        :", [j + 1 for j in a.unassigned_cols])
print("total profit              :", a.cost)
