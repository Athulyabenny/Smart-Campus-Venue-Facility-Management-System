"""
Smart Campus Algorithmic Engine: Phase 4 Basic Algorithmic Problem Solving
File: core/algorithmic_problem_solving.py

Implements 3 classic algorithmic paradigms integrated into campus operations:
1. Greedy Technique:       Activity Selection (Maximum Non-Overlapping Venue Bookings)
2. Dynamic Programming:    0/1 Knapsack (Campus Equipment & Festival Budget Optimization)
3. Backtracking:           Timetable & Exam Hall Scheduling (Conflict-Free Constraint Satisfaction)
"""

from typing import Any, Dict, List, Optional, Set, Tuple


# =============================================================================
# 1. GREEDY TECHNIQUE: ACTIVITY SELECTION (MAXIMUM EVENT SCHEDULING)
# =============================================================================

class Activity:
    """Represents a proposed campus event requesting a venue slot."""

    def __init__(self, activity_id: str, title: str, start: int, finish: int, organizer: str = ""):
        self.activity_id: str = activity_id
        self.title: str = title
        self.start: int = start
        self.finish: int = finish
        self.organizer: str = organizer

    def to_dict(self) -> dict:
        return {
            "id": self.activity_id,
            "title": self.title,
            "start": self.start,
            "finish": self.finish,
            "organizer": self.organizer
        }

    def __repr__(self) -> str:
        return f"Activity({self.activity_id}: '{self.title}' [{self.start} - {self.finish}])"


def greedy_activity_selection(activities: List[Activity]) -> Tuple[List[Activity], int]:
    """
    Greedy Interval Scheduling: Selects the maximum size set of mutually compatible activities.
    
    Greedy Choice Property:
    Sort activities by finish time. Always pick the activity that finishes earliest,
    leaving maximum remaining time for subsequent activities.

    Time Complexity: O(n log n) for sorting + O(n) scan = O(n log n).
    Returns: (selected_activities: List[Activity], count: int)
    """
    if not activities:
        return [], 0

    # Sort activities by finish time ascending
    sorted_activities = sorted(activities, key=lambda a: a.finish)

    selected: List[Activity] = []
    # Always pick the first activity that finishes earliest
    last_finish = -1

    for act in sorted_activities:
        if act.start >= last_finish:
            selected.append(act)
            last_finish = act.finish

    return selected, len(selected)


# =============================================================================
# 2. DYNAMIC PROGRAMMING: 0/1 KNAPSACK FOR CAMPUS BUDGET OPTIMIZATION
# =============================================================================

class BudgetItem:
    """Represents a proposal or equipment item requiring campus funding."""

    def __init__(self, item_id: str, name: str, cost: int, utility_score: int):
        self.item_id: str = item_id
        self.name: str = name
        self.cost: int = cost
        self.utility_score: int = utility_score

    def to_dict(self) -> dict:
        return {
            "id": self.item_id,
            "name": self.name,
            "cost": self.cost,
            "utility_score": self.utility_score
        }

    def __repr__(self) -> str:
        return f"BudgetItem({self.name}, Cost={self.cost}, Utility={self.utility_score})"


def knapsack_budget_optimizer(
    items: List[BudgetItem],
    budget_capacity: int
) -> Tuple[int, List[BudgetItem], List[List[int]]]:
    """
    Solves 0/1 Knapsack via Dynamic Programming to maximize student utility within a fixed budget.

    DP Recurrence:
    DP[i][w] = DP[i-1][w]                                    if item.cost > w
    DP[i][w] = max(DP[i-1][w], DP[i-1][w - cost] + utility)   if item.cost <= w

    Time Complexity:  O(n * W)
    Space Complexity: O(n * W)
    Returns: (max_utility: int, chosen_items: List[BudgetItem], dp_table: List[List[int]])
    """
    n = len(items)
    W = budget_capacity

    # dp[i][w] stores maximum utility achievable using subset of first i items with budget w
    dp = [[0 for _ in range(W + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        item = items[i - 1]
        for w in range(W + 1):
            if item.cost <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - item.cost] + item.utility_score)
            else:
                dp[i][w] = dp[i - 1][w]

    max_utility = dp[n][W]

    # Backtrack to identify selected items
    chosen_items: List[BudgetItem] = []
    curr_w = W
    for i in range(n, 0, -1):
        if dp[i][curr_w] != dp[i - 1][curr_w]:
            item = items[i - 1]
            chosen_items.append(item)
            curr_w -= item.cost

    chosen_items.reverse()
    return max_utility, chosen_items, dp


# =============================================================================
# 3. BACKTRACKING: EXAM HALL & TIMETABLE CONFLICT-FREE SCHEDULING
# =============================================================================

def solve_timetable_backtracking(
    courses: List[str],
    conflict_graph: Dict[str, Set[str]],
    available_slots: List[str]
) -> Tuple[bool, Dict[str, str], int]:
    """
    Constraint Satisfaction Problem (CSP) solved via Backtracking (Graph K-Coloring).
    Assigns each course to an available timeslot / hall such that no two conflicting courses
    share the same slot.

    Parameters:
        courses: List of course codes (e.g. ['MCA101', 'MCA102', 'CS301'])
        conflict_graph: Dict mapping course -> set of conflicting courses (shared students)
        available_slots: List of timeslot labels (e.g. ['Slot 1 (9 AM)', 'Slot 2 (11 AM)', 'Slot 3 (2 PM)'])

    Returns:
        (success: bool, assignment: Dict[str, str], backtracks_count: int)
    """
    assignment: Dict[str, str] = {}
    backtracks_counter = [0]

    def _is_safe(course: str, slot: str) -> bool:
        # Check if any conflicting neighbor is already scheduled in this slot
        for neighbor in conflict_graph.get(course, set()):
            if neighbor in assignment and assignment[neighbor] == slot:
                return False
        return True

    def _backtrack(index: int) -> bool:
        if index == len(courses):
            return True  # All courses successfully scheduled

        course = courses[index]

        for slot in available_slots:
            if _is_safe(course, slot):
                assignment[course] = slot

                if _backtrack(index + 1):
                    return True

                # Backtrack
                del assignment[course]
                backtracks_counter[0] += 1

        return False

    success = _backtrack(0)
    return success, assignment, backtracks_counter[0]
