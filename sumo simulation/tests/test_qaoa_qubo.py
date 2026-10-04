import unittest
import itertools
import numpy as np
from backend.vrp.qaoa_vrp import QAOAVRPSolver


class TestQAOAQUBOFormulation(unittest.TestCase):
    """
    Unit tests verifying the mathematical correctness and physical consistency
    of the closed-tour position-variable QUBO formulation.
    """

    def setUp(self):
        self.solver = QAOAVRPSolver()
        self.cost_matrix = {
            (0, 1): 10.0, (0, 2): 15.0, (0, 3): 20.0,
            (1, 0): 10.0, (2, 0): 15.0, (3, 0): 20.0,
            (1, 2): 5.0,  (2, 1): 5.0,
            (2, 3): 8.0,  (3, 2): 8.0,
            (1, 3): 12.0, (3, 1): 12.0,
        }

    def test_qubo_energy_equals_closed_tour_cost(self):
        """
        Verify that for all valid permutations pi, the QUBO energy
        x^T Q x + linear^T x + offset exactly equals the closed-tour cost
        c_{0, pi_0} + sum c_{pi_p, pi_{p+1}} + c_{pi_{N-1}, 0}.
        """
        N = 3
        Q, linear, offset, P = self.solver._build_position_vrp_qubo(N, self.cost_matrix)

        for perm in itertools.permutations([1, 2, 3]):
            x = np.zeros(N * N)
            for p, cust in enumerate(perm):
                i = cust - 1
                x[i * N + p] = 1.0

            energy = float(x.T @ Q @ x + linear.T @ x + offset)
            true_cost = (
                self.cost_matrix[(0, perm[0])]
                + self.cost_matrix[(perm[0], perm[1])]
                + self.cost_matrix[(perm[1], perm[2])]
                + self.cost_matrix[(perm[2], 0)]
            )
            self.assertAlmostEqual(
                energy,
                true_cost,
                places=6,
                msg=f"Mismatch for permutation {perm}: QUBO={energy}, True={true_cost}",
            )

    def test_infeasible_penalty_gap(self):
        """
        Verify that any infeasible bitstring (violating row/column uniqueness)
        receives a penalty making its energy strictly higher than the maximum
        feasible tour cost.
        """
        N = 3
        Q, linear, offset, P = self.solver._build_position_vrp_qubo(N, self.cost_matrix)

        max_feasible_cost = max(
            (
                self.cost_matrix[(0, perm[0])]
                + self.cost_matrix[(perm[0], perm[1])]
                + self.cost_matrix[(perm[1], perm[2])]
                + self.cost_matrix[(perm[2], 0)]
            )
            for perm in itertools.permutations([1, 2, 3])
        )

        # Infeasible case 1: customer 1 visited at both position 0 and position 1
        x_infeasible = np.zeros(N * N)
        x_infeasible[0 * N + 0] = 1.0  # cust 1 at pos 0
        x_infeasible[0 * N + 1] = 1.0  # cust 1 at pos 1
        x_infeasible[1 * N + 2] = 1.0  # cust 2 at pos 2
        # cust 3 never visited

        energy = float(x_infeasible.T @ Q @ x_infeasible + linear.T @ x_infeasible + offset)
        self.assertGreater(
            energy,
            max_feasible_cost,
            f"Infeasible solution energy ({energy}) must exceed max feasible cost ({max_feasible_cost})",
        )


if __name__ == "__main__":
    unittest.main()
