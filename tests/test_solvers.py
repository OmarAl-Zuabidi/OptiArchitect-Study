"""
OptiArchitect Comprehensive Test Suite
======================================
Tests all modules (LP, NLP, Transportation, Assignment) to ensure 
complete code coverage and robust functionality.
"""

import unittest
import numpy as np

from optiarchitect.core import (
    solve_lp,
    solve_transportation,
    hungarian,
    golden_section,
    fibonacci_search,
    bisection_search,
    newton_raphson,
    secant_method,
)


class TestOptiArchitect(unittest.TestCase):

    def test_lp_solver(self):
        """Test Linear Programming solver (Simplex / Two-Phase)."""
        c = np.array([3.0, 5.0])
        A = np.array([
            [1.0, 0.0],
            [0.0, 2.0],
            [3.0, 2.0]
        ])
        b = np.array([4.0, 12.0, 18.0])
        con_types = ["<=", "<=", "<="]
        
        result = solve_lp(c=c, A=A, b=b, con_types=con_types, obj_type="max", method="two_phase")
        self.assertEqual(result.status, "optimal")
        self.assertAlmostEqual(result.z, 36.0, places=4)

    def test_transportation_solver(self):
        """Test Transportation Problem solver (IBFS + MODI)."""
        C = np.array([
            [2.0, 3.0, 1.0],
            [5.0, 4.0, 8.0],
            [5.0, 6.0, 8.0]
        ])
        Supply = np.array([100.0, 200.0, 150.0])
        Demand = np.array([120.0, 80.0, 250.0])
        
        res = solve_transportation(C, Supply, Demand, start="best")
        self.assertEqual(res.solution.status, "optimal")
        self.assertGreater(res.solution.cost, 0)

    def test_assignment_solver(self):
        """Test Hungarian Algorithm for Assignment Problems."""
        C = np.array([
            [9.0, 2.0, 7.0, 8.0],
            [6.0, 4.0, 3.0, 7.0],
            [5.0, 8.0, 1.0, 8.0],
            [7.0, 6.0, 9.0, 4.0]
        ])
        res = hungarian(C, maximize=False)
        self.assertIsNotNone(res.assignment)
        self.assertAlmostEqual(res.cost, 13.0, places=4)

    def test_nlp_golden_section(self):
        """Test Golden Section Search for NLP."""
        f = lambda x: (x - 2)**2 + 1
        res = golden_section(f, 0.0, 5.0, tol=1e-4)
        self.assertEqual(res.status, "converged")  # تم التعديل هنا
        self.assertAlmostEqual(res.x, 2.0, places=3)

    def test_nlp_fibonacci(self):
        """Test Fibonacci Search for NLP."""
        f = lambda x: (x - 2)**2 + 1
        res = fibonacci_search(f, 0.0, 5.0, tol=1e-4, n_eval=15)
        self.assertEqual(res.status, "converged")  # تم التعديل هنا
        self.assertAlmostEqual(res.x, 2.0, places=2)

    def test_nlp_bisection(self):
        """Test Bisection Search (Derivative-based) for NLP."""
        f = lambda x: (x - 2)**2 + 1
        df = lambda x: 2 * (x - 2)
        res = bisection_search(f, df, 0.0, 5.0, tol=1e-4)
        self.assertEqual(res.status, "converged")  # تم التعديل هنا
        self.assertAlmostEqual(res.x, 2.0, places=3)

    def test_nlp_newton_raphson(self):
        """Test Newton-Raphson Method for NLP."""
        f = lambda x: (x - 2)**2 + 1
        df = lambda x: 2 * (x - 2)
        d2f = lambda x: 2.0
        res = newton_raphson(f, df, d2f, x0=0.0, tol=1e-5)
        self.assertEqual(res.status, "converged")  # تم التعديل هنا
        self.assertAlmostEqual(res.x, 2.0, places=3)

    def test_nlp_secant(self):
        """Test Secant Method for NLP."""
        f = lambda x: (x - 2)**2 + 1
        df = lambda x: 2 * (x - 2)
        res = secant_method(f, df, x0=0.0, x1=1.0, tol=1e-5)
        self.assertEqual(res.status, "converged")  # تم التعديل هنا
        self.assertAlmostEqual(res.x, 2.0, places=3)


if __name__ == "__main__":
    unittest.main()