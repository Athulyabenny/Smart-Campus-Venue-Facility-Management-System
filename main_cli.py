"""
Smart Campus Venue & Facility Management: Interactive Terminal CLI
File: cli/main_cli.py

Provides a command-line interface for viva examinations, demonstrations,
and algorithmic inspection of custom data structures applied strictly to Venue Management.
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.venue_service import VenueService
from services.booking_service import BookingService
from services.navigation_service import NavigationService

from core.bst import BinarySearchTree
from core.searching_sorting import (
    linear_search,
    binary_search,
    merge_sort,
    quick_sort,
    insertion_sort,
    compare_sorting_algorithms,
)
from core.algorithmic_problem_solving import (
    Activity,
    greedy_activity_selection,
    BudgetItem,
    knapsack_budget_optimizer,
    solve_timetable_backtracking,
)


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    PURPLE = "\033[95m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"


def print_banner():
    print(f"""{Colors.CYAN}{Colors.BOLD}
================================================================================
   SMART CAMPUS VENUE & FACILITY MANAGEMENT: ALGORITHMIC ENGINE (MCA DSA)
================================================================================{Colors.RESET}
  [1] Phase 1: Linear Data Structures (CLO1)      --> Venue Linked List, Stack, Queue, Setup Score Evaluator
  [2] Phase 2: Hierarchical & Graph DSA (CLO2)    --> Venue BST, Traversals, 3 Deletion Cases, BFS/DFS
  [3] Phase 3: Searching & Sorting (CLO2)         --> Linear/Binary Search, Merge/Quick Sort on Venues
  [4] Phase 4: Basic Algorithmic Solvers (CLO3)   --> Greedy Activity, 0/1 Knapsack, Timetable Backtracking
  [5] Expected Deliverable: R Venue Analytics     --> Regression, Capacity EDA, Utilization Modeling
  [6] Venue & Slot Booking Engine                 --> Augmented Interval Tree [O(log n + k) Clash Detection]
  [7] VIP Priority Event Allocation               --> Binary Max-Heap Priority Queue [O(log n) Extract-Max]
  [8] Campus Venue Wayfinding                     --> Adjacency List + Min-Heap Dijkstra
  [9] Algorithmic Performance Benchmarks
  [10] Exit System
--------------------------------------------------------------------------------""")


class CampusCLI:

    def __init__(self):
        data_dir = os.path.join(PROJECT_ROOT, "data")
        self.venue_service = VenueService(data_dir=data_dir)
        self.booking_service = BookingService(data_dir=data_dir)
        self.navigation_service = NavigationService(data_dir=data_dir)

    def run(self):
        while True:
            print_banner()
            choice = input(f"{Colors.YELLOW}Select an operation (1-10): {Colors.RESET}").strip()
            if choice == "1":
                self.phase1_linear_menu()
            elif choice == "2":
                self.phase2_hierarchical_menu()
            elif choice == "3":
                self.phase3_search_sort_menu()
            elif choice == "4":
                self.phase4_algorithms_menu()
            elif choice == "5":
                self.r_deliverable_menu()
            elif choice == "6":
                self.venue_interval_tree_menu()
            elif choice == "7":
                self.priority_heap_menu()
            elif choice == "8":
                self.navigation_menu()
            elif choice == "9":
                self.benchmarks_menu()
            elif choice == "10":
                print(f"{Colors.GREEN}Terminating Smart Campus Engine. Goodbye!{Colors.RESET}")
                break
            else:
                print(f"{Colors.RED}Invalid selection. Please choose 1-10.{Colors.RESET}")

    def phase1_linear_menu(self):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}--- Phase 1: Linear Data Structures ---{Colors.RESET}")
        print("  [1] Display All Venues (Singly Linked List Traversal)")
        print("  [2] Register New Venue (Insert Head / Tail)")
        print("  [3] Delete Venue by Code (O(n) Traversal & Delete)")
        print("  [4] Reverse Venue List (In-Place O(n) Time, O(1) Space)")
        print("  [5] Undo Last Venue Operation (Custom LinkedStack LIFO)")
        print("  [6] Issue Waitlist Token (Custom LinkedQueue FIFO)")
        print("  [7] Serve Next Waitlist Request (Dequeue FIFO)")
        print("  [8] Evaluate Facility Setup Score (Shunting-Yard Stack)")
        c = input("Enter choice (1-8): ").strip()

        if c == "1":
            venues = self.venue_service.get_all_venues()
            print(f"\nTotal Registered Venues: {len(venues)}")
            for idx, v in enumerate(venues, 1):
                ac_status = "AC" if v.air_conditioned else "Non-AC"
                projector_status = "Projector" if v.projector else "No Projector"
                print(
                    f"  {idx}. [{v.venue_id}] {v.name} ({v.building}) - "
                    f"Category: {v.category}, Capacity: {v.capacity}, "
                    f"{ac_status}, {projector_status}"
                )
        elif c == "2":
            vid = input("Venue ID: ").strip()
            name = input("Venue Name: ").strip()
            bld = input("Building: ").strip()
            cap = int(input("Capacity: ").strip() or "100")
            at_front = input("Insert at Head? (y/N): ").strip().lower() == "y"
            rec = self.venue_service.add_venue(vid, name, bld, capacity=cap, at_front=at_front)
            self.booking_service.register_venue(vid, name, cap, bld)
            print(f"{Colors.GREEN}Registered venue: {rec}{Colors.RESET}")
        elif c == "3":
            vid = input("Enter Venue ID to delete: ").strip()
            if self.venue_service.delete_venue(vid):
                print(f"{Colors.GREEN}Deleted '{vid}'.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Venue not found.{Colors.RESET}")
        elif c == "4":
            self.venue_service.reverse_venue_list()
            print(f"{Colors.GREEN}Venue Linked List reversed in-place.{Colors.RESET}")
        elif c == "5":
            ok, msg = self.venue_service.undo_last_operation()
            print(f"{Colors.GREEN if ok else Colors.RED}{msg}{Colors.RESET}")
        elif c == "6":
            title = input("Event Title: ").strip()
            vid = input("Venue ID: ").strip() or "auditorium_main"
            item = self.venue_service.enqueue_waitlist_request("REQ-CLI", vid, title, "Student Club", "14:00 - 17:00")
            print(f"{Colors.GREEN}Enqueued Token {item['token']}.{Colors.RESET}")
        elif c == "7":
            item = self.venue_service.dequeue_waitlist_request()
            if item:
                print(f"{Colors.GREEN}Approved Token {item['token']} for '{item['title']}'.{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}Waitlist is empty.{Colors.RESET}")
        elif c == "8":
            attendees = float(input("Expected attendees (default 300): ").strip() or "300")
            hours = float(input("Event duration in hours (default 2.5): ").strip() or "2.5")
            av_units = float(input("AV equipment units (default 40): ").strip() or "40")
            buffer_percent = float(input("Setup buffer % (default 10): ").strip() or "10")
            res = self.venue_service.calculate_resource_score(
                attendees, hours, av_units, buffer_percent
            )
            if res.get("success"):
                print(
                    f"{Colors.GREEN}Facility Setup Readiness Score: "
                    f"{res['setup_score']} units [Formula: {res['formula']}]{Colors.RESET}"
                )
            else:
                print(f"{Colors.RED}Error: {res.get('error')}{Colors.RESET}")

    def phase2_hierarchical_menu(self):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}--- Phase 2: Hierarchical (BST) & Graph Traversals ---{Colors.RESET}")
        traversals = self.venue_service.get_bst_traversals()
        print(f"BST Nodes: {traversals['size']}, Height: {traversals['height']}")
        print(f"\n{Colors.CYAN}Inorder Traversal (Sorted Keys):{Colors.RESET}")
        for n in traversals['inorder']:
            print(f"  • Key: {n['key']} -> {n['value']['name']} (Cap: {n['value']['capacity']})")

    def phase3_search_sort_menu(self):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}--- Phase 3: Searching & Sorting on Venues ---{Colors.RESET}")
        venues = self.venue_service.get_all_venues()
        raw = [v.to_dict() for v in venues]
        print(f"Total Records: {len(raw)}")
        bench = compare_sorting_algorithms(raw, key_func=lambda x: x["capacity"], runs=3)
        print(f"\n{Colors.CYAN}Sorting Benchmark on Venue Capacity:{Colors.RESET}")
        print(f"Average runtime over {bench['runs']} runs:")
        for stats in bench["results"]:
            print(f"  • {stats['algorithm']:<16}: {stats['time_ms']:.4f} ms")

    def phase4_algorithms_menu(self):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}--- Phase 4: Algorithmic Problem Solving ---{Colors.RESET}")
        print("  [1] Greedy Activity Selection (Earliest Finish Time First)")
        print("  [2] 0/1 Knapsack DP (Venue AV Equipment Budget Optimizer)")
        print("  [3] Backtracking Timetable CSP (Exam Hall Conflict Avoidance)")
        c = input("Select solver (1-3): ").strip()
        if c == "1":
            acts = [
                Activity("EV-01", "Tech Symposium Keynote", 9.0, 11.0),
                Activity("EV-02", "Workshop on GenAI", 10.0, 12.5),
                Activity("EV-03", "Industry Panel Discussion", 11.0, 13.0),
                Activity("EV-04", "Alumni Networking Lunch", 12.5, 14.0),
                Activity("EV-05", "Valedictory & Awards", 13.5, 15.5)
            ]
            selected, _ = greedy_activity_selection(acts)
            print(f"{Colors.GREEN}Selected {len(selected)} non-conflicting activities:{Colors.RESET}")
            for a in selected:
                print(f"  • {a.title} ({a.start:.1f} to {a.finish:.1f})")
        elif c == "2":
            items = [
                BudgetItem("EQ-01", "Laser 4K Projector", 40, 85),
                BudgetItem("EQ-02", "Line Array Audio Rig", 50, 95),
                BudgetItem("EQ-03", "Wireless Lapel Mic Set", 20, 45),
                BudgetItem("EQ-04", "PTZ Streaming Camera", 30, 70),
                BudgetItem("EQ-05", "Interactive Podium", 35, 65)
            ]
            cap = 90
            max_u, chosen, _ = knapsack_budget_optimizer(items, cap)
            print(f"{Colors.GREEN}Max Utility: {max_u} (Budget Limit: {cap}){Colors.RESET}")
            for it in chosen:
                print(f"  • {it.name} (Cost: {it.cost}, Utility: +{it.utility_score})")
        elif c == "3":
            courses = ["MCA-DSA", "MCA-ADBMS", "MCA-Cloud", "MCA-ML"]
            conflicts = {
                "MCA-DSA": {"MCA-ADBMS", "MCA-ML"},
                "MCA-ADBMS": {"MCA-DSA", "MCA-Cloud"},
                "MCA-Cloud": {"MCA-ADBMS"},
                "MCA-ML": {"MCA-DSA"}
            }
            slots = ["Hall A", "Hall B"]
            ok, sched, steps = solve_timetable_backtracking(courses, conflicts, slots)
            if ok:
                print(f"{Colors.GREEN}Schedule found in {steps} backtracking steps:{Colors.RESET}")
                for crs, h in sched.items():
                    print(f"  • {crs} -> {h}")
            else:
                print(f"{Colors.RED}No conflict-free schedule possible.{Colors.RESET}")

    def r_deliverable_menu(self):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}--- Expected Deliverable: R Venue Analytics ---{Colors.RESET}")
        print("  • Script: analytics/campus_analytics.R")
        print("  • Dataset: data/venue_analytics_dataset.csv")
        print("  • Models: Linear Regression (Utilization ~ Capacity + Duration) & Logistic Regression (High Efficiency)")

    def venue_interval_tree_menu(self):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}--- Venue Booking: Augmented AVL Interval Tree ---{Colors.RESET}")
        vid = input("Enter Venue ID (default auditorium_main): ").strip() or "auditorium_main"
        bookings = self.booking_service.get_venue_schedule(vid)
        print(f"Existing bookings for '{vid}':")
        for b in bookings:
            print(f"  • [{b.booking_id}] {b.title}: {b.start_time_str} - {b.end_time_str}")

        print("\nTest Conflict Detection:")
        s = input("Start time (HH:MM): ").strip()
        e = input("End time (HH:MM): ").strip()
        s_min = BookingService.time_str_to_minutes(s)
        e_min = BookingService.time_str_to_minutes(e)
        clashes = self.booking_service.check_clashes(vid, s_min, e_min)
        if clashes:
            print(f"{Colors.RED}CLASH DETECTED with {len(clashes)} booking(s):{Colors.RESET}")
            for c in clashes:
                print(f"  - '{c.title}' ({c.start_time_str} - {c.end_time_str})")
        else:
            print(f"{Colors.GREEN}SLOT FREE! Zero conflicts in O(log n + k).{Colors.RESET}")

    def priority_heap_menu(self):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}--- VIP Priority Event Allocation (Max-Heap) ---{Colors.RESET}")
        reqs = self.venue_service.get_all_priority_requests()
        for r in reqs:
            print(f"  • [{r['request_id']}] Priority: {r['priority_score']} - '{r['title']}' ({r['venue_id']})")
        top = self.venue_service.extract_highest_priority()
        if top:
            print(f"{Colors.GREEN}Dispatched Top Priority via Extract-Max: '{top['title']}' (Score: {top['priority_score']}){Colors.RESET}")

    def navigation_menu(self):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}--- Campus Venue Wayfinding (Graph + Min-Heap Dijkstra) ---{Colors.RESET}")
        route = self.navigation_service.find_route("main_gate", "auditorium_main", accessible_only=True)
        if route:
            print(f"{Colors.GREEN}Walking Route to Main Auditorium: {route['total_distance_m']}m{Colors.RESET}")
            for idx, pt in enumerate(route["path"], 1):
                print(f"  {idx}. {pt['name']} ({pt['node_id']})")

    def benchmarks_menu(self):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}--- Algorithmic Benchmarks ---{Colors.RESET}")
        from benchmarks.performance_benchmark import run_full_benchmark_suite
        run_full_benchmark_suite()


def main():
    cli = CampusCLI()
    cli.run()


if __name__ == "__main__":
    main()
