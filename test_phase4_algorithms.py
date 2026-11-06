"""
Unit Tests for Phase 4: Basic Algorithmic Problem Solving
File: tests/test_phase4_algorithms.py
"""

import unittest
from core.algorithmic_problem_solving import (
    Activity,
    greedy_activity_selection,
    BudgetItem,
    knapsack_budget_optimizer,
    solve_timetable_backtracking,
)


class TestPhase4Algorithms(unittest.TestCase):

    def test_greedy_activity_selection(self):
        # 6 proposed campus events with (start, finish)
        activities = [
            Activity("A1", "Robotics Workshop", 1, 4),
            Activity("A2", "AI Seminar", 3, 5),
            Activity("A3", "Coding Contest", 0, 6),
            Activity("A4", "Guest Lecture", 5, 7),
            Activity("A5", "Cultural Practice", 3, 9),
            Activity("A6", "Valedictory", 5, 9),
            Activity("A7", "Sports Meet", 6, 10),
            Activity("A8", "Alumni Talk", 8, 11),
            Activity("A9", "Hackathon Pitch", 8, 12),
            Activity("A10", "Music Jam", 2, 14),
            Activity("A11", "Quiz Competition", 12, 16)
        ]

        selected, count = greedy_activity_selection(activities)
        # Optimal schedule: [A1 (1-4), A4 (5-7), A8 (8-11), A11 (12-16)] -> count 4
        self.assertEqual(count, 4)
        selected_ids = [a.activity_id for a in selected]
        self.assertEqual(selected_ids, ["A1", "A4", "A8", "A11"])

    def test_knapsack_budget_optimizer(self):
        # Budget = 50 (in thousands Rs.)
        # Items: (name, cost, utility)
        items = [
            BudgetItem("B1", "New Lab Workstations", 20, 40),
            BudgetItem("B2", "Robotics Kit Pack", 15, 30),
            BudgetItem("B3", "Digital Library Subscription", 30, 60),
            BudgetItem("B4", "Auditorium Projector", 10, 25),
            BudgetItem("B5", "Campus IoT Gateway", 25, 35)
        ]
        budget = 50

        max_util, chosen, _ = knapsack_budget_optimizer(items, budget)
        # B3 (30, 60) + B1 (20, 40) = cost 50, utility 100
        # B3 (30, 60) + B4 (10, 25) + B2 (15, 30) = cost 55 (exceeds 50)
        # Optimal: B1 + B3 or B2 + B3 + ... Wait:
        # B3(30, 60) + B4(10, 25) = cost 40, util 85.
        # B1(20, 40) + B2(15, 30) + B4(10, 25) = cost 45, util 95.
        # B1(20, 40) + B3(30, 60) = cost 50, util 100.
        self.assertEqual(max_util, 100)
        total_cost = sum(it.cost for it in chosen)
        self.assertLessEqual(total_cost, budget)
        self.assertEqual(sum(it.utility_score for it in chosen), 100)

    def test_backtracking_timetable(self):
        courses = ["MCA101", "MCA102", "CS201", "AI301"]
        # MCA101 conflicts with MCA102 and CS201
        # MCA102 conflicts with MCA101 and AI301
        conflicts = {
            "MCA101": {"MCA102", "CS201"},
            "MCA102": {"MCA101", "AI301"},
            "CS201": {"MCA101"},
            "AI301": {"MCA102"}
        }
        slots = ["9:00 AM - Slot A", "11:00 AM - Slot B"]

        success, assignment, backtracks = solve_timetable_backtracking(courses, conflicts, slots)
        self.assertTrue(success)
        self.assertEqual(len(assignment), 4)

        # Verify no conflicting courses have the same slot
        for c1, conflicting_set in conflicts.items():
            for c2 in conflicting_set:
                self.assertNotEqual(
                    assignment[c1], assignment[c2],
                    f"Conflict violation: {c1} and {c2} both assigned to {assignment[c1]}"
                )


if __name__ == "__main__":
    unittest.main()
