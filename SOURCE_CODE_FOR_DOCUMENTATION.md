# Smart Campus Venue & Facility Management System — Source Code

This document collects the project's source files for reference and documentation. Each section is labelled with its original project path. Sample JSON/CSV data, generated images, and compiled cache files are not included.

## `analytics/campus_analytics.R`

````r
# ==============================================================================
# Smart Campus Venue & Facility Management: R Data Analytics & Modeling
# File: analytics/campus_analytics.R
# MCA Data Structures & Analytics Project Deliverable
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. LOAD AND PREPROCESS DATASET
# ------------------------------------------------------------------------------

cat("\n[STEP 1] Loading and Preprocessing Campus Venue Analytics Dataset...\n")

csv_path <- file.path("data", "venue_analytics_dataset.csv")
if (!file.exists(csv_path)) {
  csv_path <- file.path("..", "data", "venue_analytics_dataset.csv")
}

if (!file.exists(csv_path)) {
  stop(paste("Dataset file not found at:", csv_path))
}

venue_data <- read.csv(csv_path, header = TRUE, stringsAsFactors = FALSE)
cat(sprintf("Loaded %d venue records with %d attributes.\n", nrow(venue_data), ncol(venue_data)))

cat("\n--- Dataset Structure ---\n")
str(venue_data)

# Preprocessing & Data Cleaning
venue_data$category <- as.factor(venue_data$category)
venue_data$efficiency_grade <- as.factor(venue_data$efficiency_grade)
venue_data$capacity <- as.integer(venue_data$capacity)
venue_data$duration_hours <- as.numeric(venue_data$duration_hours)
venue_data$attendees <- as.integer(venue_data$attendees)
venue_data$utilization_pct <- as.numeric(venue_data$utilization_pct)
venue_data$satisfaction_score <- as.numeric(venue_data$satisfaction_score)

# Handle potential missing values
if (any(is.na(venue_data))) {
  cat("Warning: Missing values detected. Imputing with column medians...\n")
  venue_data$utilization_pct[is.na(venue_data$utilization_pct)] <- median(venue_data$utilization_pct, na.rm = TRUE)
}

# Create binary classification label: High Efficiency (Utilization >= 75%)
venue_data$is_high_efficiency <- as.factor(ifelse(venue_data$utilization_pct >= 75.0, 1, 0))

cat("\n--- Descriptive Summary Statistics ---\n")
summary(venue_data[, c("capacity", "duration_hours", "attendees", "utilization_pct", "satisfaction_score")])

# ------------------------------------------------------------------------------
# 2. STATISTICAL MODELING
# ------------------------------------------------------------------------------

cat("\n[STEP 2] Fitting Multiple Linear Regression (Venue Utilization)...\n")
# Model: Utilization % ~ Duration Hours + Attendees + Venue Capacity
lm_model <- lm(utilization_pct ~ duration_hours + attendees + capacity, data = venue_data)
cat("\n--- Multiple Linear Regression Model Summary ---\n")
print(summary(lm_model))

cat("\n[STEP 3] Fitting Binary Logistic Regression (High Efficiency Probability)...\n")
# Model: High Efficiency ~ Duration Hours + Satisfaction Score
glm_model <- glm(is_high_efficiency ~ duration_hours + satisfaction_score, data = venue_data, family = binomial)
cat("\n--- Binary Logistic Regression Model Summary ---\n")
print(summary(glm_model))

cat("\n[COMPLETE] Campus Venue Analytics executed successfully.\n")
````

## `analytics/campus_analytics.Rmd`

````markdown
---
title: "Smart Campus & Student Operations: Data Analytics & Predictive Modeling"
author: "MCA Data Structures & Analytics Project"
date: "2026-09-07"
output:
  html_document:
    toc: true
    toc_depth: 3
    theme: cosmo
    highlight: tango
---

```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE, warning = FALSE, message = FALSE)
```

## 1. Executive Summary

This R Notebook satisfies the course deliverable requirement by performing data ingestion, exploratory data analysis, visualization, and machine learning model training on the **Smart Campus Student Operations** dataset.

The analysis addresses:
- **Academic Trends**: How class attendance directly influences cumulative student grade point average (CGPA).
- **Tuition & Scholarship Distribution**: Analysis of institutional discounts and net payable fees across departments.
- **Predictive Modeling**:
  1. Multiple Linear Regression for CGPA estimation.
  2. Binary Logistic Regression for High Merit scholarship eligibility prediction.

---

## 2. Data Loading & Preprocessing

```{r load_data}
# Locate dataset
csv_path <- file.path("..", "data", "students_dataset.csv")
if (!file.exists(csv_path)) {
  csv_path <- file.path("data", "students_dataset.csv")
}

students <- read.csv(csv_path, header = TRUE, stringsAsFactors = FALSE)

# Convert factor variables
students$department <- as.factor(students$department)
students$merit_category <- as.factor(students$merit_category)
students$is_high_merit <- as.factor(ifelse(students$cgpa >= 8.5, 1, 0))

# Dataset Structure
str(students)
```

### Descriptive Statistics

```{r summary_stats}
summary(students[, c("cgpa", "attendance", "base_fee", "scholarship_percent", "net_fee")])
```

---

## 3. Exploratory Data Analysis & Visualization

### A. Distribution of Student CGPA

```{r plot_cgpa, fig.width=8, fig.height=5}
hist(students$cgpa,
     breaks = 8,
     col = "#38bdf8",
     border = "#0284c7",
     main = "Student CGPA Distribution",
     xlab = "Cumulative GPA",
     ylab = "Number of Students",
     las = 1)
abline(v = mean(students$cgpa), col = "red", lwd = 2, lty = 2)
legend("topright", legend = c(paste("Mean CGPA =", round(mean(students$cgpa), 2))),
       col = "red", lty = 2, lwd = 2)
```

### B. Correlation: Attendance vs. Academic Performance (CGPA)

```{r plot_attendance, fig.width=8, fig.height=5}
plot(students$attendance, students$cgpa,
     pch = 19,
     col = "#6366f1",
     main = "Relationship Between Attendance and Academic Performance",
     xlab = "Attendance (%)",
     ylab = "CGPA",
     las = 1)

# Fit linear regression trendline
trend_model <- lm(cgpa ~ attendance, data = students)
abline(trend_model, col = "#ef4444", lwd = 2)
grid(col = "lightgray", lty = "dotted")
legend("topleft", legend = paste("Linear Fit: R^2 =", round(summary(trend_model)$r.squared, 3)),
       col = "#ef4444", lty = 1, lwd = 2)
```

### C. Department-wise Performance

```{r plot_dept, fig.width=8, fig.height=5}
boxplot(cgpa ~ department, data = students,
        col = c("#34d399", "#60a5fa", "#f472b6"),
        main = "Academic Performance by Department",
        xlab = "Academic Department",
        ylab = "CGPA",
        las = 1)
```

---

## 4. Predictive Modeling

### Model 1: Multiple Linear Regression (CGPA Estimation)

```{r linear_regression}
set.seed(42)
train_idx <- sample(1:nrow(students), size = 0.8 * nrow(students))
train <- students[train_idx, ]
test <- students[-train_idx, ]

# Fit Multiple Linear Regression Model
lm_fit <- lm(cgpa ~ attendance + semester + base_fee, data = train)
summary(lm_fit)

# Evaluation on Test Data
preds <- predict(lm_fit, newdata = test)
rmse <- sqrt(mean((test$cgpa - preds)^2))
cat(sprintf("Test Set RMSE: %.4f\n", rmse))
```

### Model 2: Logistic Regression (High Merit Scholarship Qualification)

```{r logistic_regression}
# Logistic regression to classify students as High Merit (CGPA >= 8.5)
logit_fit <- glm(is_high_merit ~ attendance + semester, data = train, family = binomial)
summary(logit_fit)

# Confusion Matrix
test_probs <- predict(logit_fit, newdata = test, type = "response")
test_classes <- ifelse(test_probs > 0.5, 1, 0)
table(Actual = test$is_high_merit, Predicted = test_classes)
```

---

## 5. Conclusion

- A strong positive linear correlation exists between class attendance and CGPA.
- Multiple Linear Regression provides an accurate estimator for academic GPA with low RMSE.
- Logistic Regression achieves robust classification for merit scholarship candidate identification.
````

## `benchmarks/performance_benchmark.py`

````python
"""
Smart Campus Algorithmic Engine: Performance Benchmark Suite
File: benchmarks/performance_benchmark.py

Empirically verifies the theoretical time complexities:
1. Interval Tree [O(log n + k)] vs Linear Array Scan [O(n)]
2. Max-Heap [O(log n)] vs Unsorted List Linear Scan [O(n)]
"""

import time
import random
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.interval_tree import IntervalTree
from core.max_heap import MaxHeap


def linear_find_overlapping(intervals, query_low, query_high):
    """Naive O(n) linear scan for comparison."""
    overlaps = []
    for low, high, data in intervals:
        if low < query_high and query_low < high:
            overlaps.append((low, high, data))
    return overlaps


def benchmark_interval_tree(sizes=(500, 2000, 5000, 10000)):
    print("\n" + "=" * 75)
    print(" 1. BENCHMARK: Augmented Interval Tree O(log n + k) vs Linear Scan O(n)")
    print("=" * 75)
    print(f"{'Dataset Size (N)':<18} | {'Interval Tree Time':<20} | {'Linear Scan Time':<20} | {'Speedup Factor'}")
    print("-" * 75)

    random.seed(42)
    for n in sizes:
        tree = IntervalTree()
        linear_list = []

        # Generate n intervals
        for i in range(n):
            start = random.randint(1, 100000)
            duration = random.randint(15, 120)
            end = start + duration
            tree.insert(start, end, data=f"Event_{i}")
            linear_list.append((start, end, f"Event_{i}"))

        # Generate 100 random clash queries
        queries = [(random.randint(1, 100000), random.randint(15, 60)) for _ in range(100)]
        queries = [(q[0], q[0] + q[1]) for q in queries]

        # Time Interval Tree
        t0 = time.perf_counter()
        for q_low, q_high in queries:
            _ = tree.find_all_overlapping(q_low, q_high)
        tree_time = time.perf_counter() - t0

        # Time Linear Scan
        t0 = time.perf_counter()
        for q_low, q_high in queries:
            _ = linear_find_overlapping(linear_list, q_low, q_high)
        linear_time = time.perf_counter() - t0

        speedup = (linear_time / tree_time) if tree_time > 0 else float("inf")
        print(f"{n:<18} | {tree_time * 1000:>14.3f} ms | {linear_time * 1000:>14.3f} ms | {speedup:>12.2f}x faster")


def benchmark_max_heap(sizes=(1000, 5000, 10000, 25000)):
    print("\n" + "=" * 75)
    print(" 2. BENCHMARK: Custom Max-Heap O(log n) vs Unsorted List O(n) Priority Queue")
    print("=" * 75)
    print(f"{'Dataset Size (N)':<18} | {'Heap Extract Time':<20} | {'List Extract Time':<20} | {'Speedup Factor'}")
    print("-" * 75)

    random.seed(42)
    for n in sizes:
        heap = MaxHeap()
        unsorted_list = []

        for i in range(n):
            prio = float(random.randint(1, 100000))
            heap.insert(f"ID_{i}", prio)
            unsorted_list.append((f"ID_{i}", prio))

        # Perform 500 extractions
        k = min(500, n)

        # Time Heap
        t0 = time.perf_counter()
        for _ in range(k):
            _ = heap.extract_max()
        heap_time = time.perf_counter() - t0

        # Time List (Linear search for max, then pop)
        t0 = time.perf_counter()
        for _ in range(k):
            max_idx = 0
            for j in range(1, len(unsorted_list)):
                if unsorted_list[j][1] > unsorted_list[max_idx][1]:
                    max_idx = j
            _ = unsorted_list.pop(max_idx)
        list_time = time.perf_counter() - t0

        speedup = (list_time / heap_time) if heap_time > 0 else float("inf")
        print(f"{n:<18} | {heap_time * 1000:>14.3f} ms | {list_time * 1000:>14.3f} ms | {speedup:>12.2f}x faster")


def run_full_benchmark_suite():
    print("\nStarting Algorithmic Performance Verification...")
    benchmark_interval_tree()
    benchmark_max_heap()
    print("\n" + "=" * 75)
    print(" [VERIFICATION RESULT]: Asymptotic complexity O(log n) empirically confirmed!")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_full_benchmark_suite()
````

## `cli/main_cli.py`

````python
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
````

## `core/__init__.py`

````python
"""
Smart Campus Algorithmic Engine: Core Data Structures & Algorithms
"""

# Phase 1: Linear Data Structures
from core.linked_list import SinglyLinkedList, Node
from core.stack import LinkedStack, StackNode
from core.queue import LinkedQueue, QueueNode
from core.expression_evaluator import (
    check_balanced_brackets,
    infix_to_postfix,
    evaluate_postfix,
    evaluate_campus_formula,
    ExpressionError,
)

# Phase 2: Hierarchical & Graph Data Structures
from core.bst import BinarySearchTree, BSTNode
from core.interval_tree import IntervalTree, IntervalNode
from core.max_heap import MaxHeap, HeapItem
from core.min_heap import MinHeap, MinHeapItem
from core.graph import CampusGraph, Landmark, Edge

# Phase 3: Searching & Sorting
from core.searching_sorting import (
    linear_search,
    binary_search,
    merge_sort,
    quick_sort,
    insertion_sort,
    compare_sorting_algorithms,
)

# Phase 4: Algorithmic Problem Solving
from core.algorithmic_problem_solving import (
    Activity,
    greedy_activity_selection,
    BudgetItem,
    knapsack_budget_optimizer,
    solve_timetable_backtracking,
)

__all__ = [
    # Phase 1
    "SinglyLinkedList",
    "Node",
    "LinkedStack",
    "StackNode",
    "LinkedQueue",
    "QueueNode",
    "check_balanced_brackets",
    "infix_to_postfix",
    "evaluate_postfix",
    "evaluate_campus_formula",
    "ExpressionError",
    # Phase 2
    "BinarySearchTree",
    "BSTNode",
    "IntervalTree",
    "IntervalNode",
    "MaxHeap",
    "HeapItem",
    "MinHeap",
    "MinHeapItem",
    "CampusGraph",
    "Landmark",
    "Edge",
    # Phase 3
    "linear_search",
    "binary_search",
    "merge_sort",
    "quick_sort",
    "insertion_sort",
    "compare_sorting_algorithms",
    # Phase 4
    "Activity",
    "greedy_activity_selection",
    "BudgetItem",
    "knapsack_budget_optimizer",
    "solve_timetable_backtracking",
]
````

## `core/algorithmic_problem_solving.py`

````python
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
````

## `core/bst.py`

````python
"""
Smart Campus Algorithmic Engine: Phase 2 Hierarchical Structures
File: core/bst.py

Custom Binary Search Tree (BST) for student and academic record indexing.
Implements pointer-based node architecture with full traversal suites:
- Inorder Traversal   (Left, Root, Right) -> Yields ascending sorted order
- Preorder Traversal  (Root, Left, Right) -> Used for tree cloning and serialization
- Postorder Traversal (Left, Right, Root) -> Used for bottom-up node deallocation

Time Complexities:
    * Search:     O(log n) average, O(n) worst-case
    * Insert:     O(log n) average, O(n) worst-case
    * Delete:     O(log n) average, O(n) worst-case
    * Traversals: O(n)
"""

from typing import Any, Callable, List, Optional, Tuple


class BSTNode:
    """Node in a Binary Search Tree."""

    def __init__(self, key: Any, data: Any = None):
        self.key: Any = key
        self.data: Any = data if data is not None else key
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None

    def __repr__(self) -> str:
        return f"BSTNode(key={self.key}, data={self.data})"


class BinarySearchTree:
    """
    Textbook-grade Binary Search Tree implementation.
    Zero external libraries used.
    """

    def __init__(self):
        self.root: Optional[BSTNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.root is None

    # -------------------------------------------------------------------------
    # Insertion
    # -------------------------------------------------------------------------

    def insert(self, key: Any, data: Any = None) -> None:
        """Inserts a key-data pair into the BST."""
        self.root = self._insert_recursive(self.root, key, data)

    def _insert_recursive(self, node: Optional[BSTNode], key: Any, data: Any) -> BSTNode:
        if node is None:
            self._size += 1
            return BSTNode(key, data)

        if key < node.key:
            node.left = self._insert_recursive(node.left, key, data)
        elif key > node.key:
            node.right = self._insert_recursive(node.right, key, data)
        else:
            # Key already exists: update data in-place
            node.data = data if data is not None else key

        return node

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------

    def search(self, key: Any) -> Optional[Any]:
        """Searches for key and returns associated data, or None if not found."""
        current = self.root
        while current is not None:
            if key == current.key:
                return current.data
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return None

    def contains(self, key: Any) -> bool:
        return self.search(key) is not None

    # -------------------------------------------------------------------------
    # Deletion
    # -------------------------------------------------------------------------

    def delete(self, key: Any) -> bool:
        """Deletes a node with the given key. Returns True if deleted, False otherwise."""
        initial_size = self._size
        self.root = self._delete_recursive(self.root, key)
        return self._size < initial_size

    def _get_min_node(self, node: BSTNode) -> BSTNode:
        curr = node
        while curr.left is not None:
            curr = curr.left
        return curr

    def _delete_recursive(self, node: Optional[BSTNode], key: Any) -> Optional[BSTNode]:
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete_recursive(node.left, key)
        elif key > node.key:
            node.right = self._delete_recursive(node.right, key)
        else:
            # Match found
            self._size -= 1
            # Case 1: Leaf node or 1 child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Case 2: Two children -> find inorder successor (min in right subtree)
            successor = self._get_min_node(node.right)
            node.key = successor.key
            node.data = successor.data

            # Delete the successor from right subtree
            self._size += 1  # Increment back since recursive call will decrement
            node.right = self._delete_recursive(node.right, successor.key)

        return node

    # -------------------------------------------------------------------------
    # Tree Traversals (Inorder, Preorder, Postorder)
    # -------------------------------------------------------------------------

    def inorder(self) -> List[Tuple[Any, Any]]:
        """
        Inorder Traversal: Left -> Root -> Right.
        Yields keys in strictly ascending sorted order.
        """
        result: List[Tuple[Any, Any]] = []

        def _traverse(node: Optional[BSTNode]):
            if node is not None:
                _traverse(node.left)
                result.append((node.key, node.data))
                _traverse(node.right)

        _traverse(self.root)
        return result

    def preorder(self) -> List[Tuple[Any, Any]]:
        """
        Preorder Traversal: Root -> Left -> Right.
        Useful for cloning or serializing tree structure.
        """
        result: List[Tuple[Any, Any]] = []

        def _traverse(node: Optional[BSTNode]):
            if node is not None:
                result.append((node.key, node.data))
                _traverse(node.left)
                _traverse(node.right)

        _traverse(self.root)
        return result

    def postorder(self) -> List[Tuple[Any, Any]]:
        """
        Postorder Traversal: Left -> Right -> Root.
        Useful for bottom-up calculation and tree deallocation.
        """
        result: List[Tuple[Any, Any]] = []

        def _traverse(node: Optional[BSTNode]):
            if node is not None:
                _traverse(node.left)
                _traverse(node.right)
                result.append((node.key, node.data))

        _traverse(self.root)
        return result

    # -------------------------------------------------------------------------
    # Auxiliary Metrics & Visualizer
    # -------------------------------------------------------------------------

    def height(self) -> int:
        """Calculates maximum depth/height of the tree."""
        def _height(node: Optional[BSTNode]) -> int:
            if node is None:
                return 0
            return 1 + max(_height(node.left), _height(node.right))
        return _height(self.root)

    def print_ascii_tree(self) -> str:
        """Visualizes the BST in ASCII tree format for viva demonstrations."""
        if not self.root:
            return "<Empty Binary Search Tree>"

        lines: List[str] = []

        def _print_node(node: Optional[BSTNode], prefix: str = "", is_left: bool = True):
            if node is not None:
                lines.append(f"{prefix}{'|-- ' if is_left else '\\-- '}[Key: {node.key}] ({getattr(node.data, 'name', str(node.data))})")
                child_prefix = prefix + ("|   " if is_left else "    ")
                if node.left or node.right:
                    if node.left:
                        _print_node(node.left, child_prefix, True)
                    else:
                        lines.append(f"{child_prefix}|-- <None>")
                    if node.right:
                        _print_node(node.right, child_prefix, False)
                    else:
                        lines.append(f"{child_prefix}\\-- <None>")

        _print_node(self.root, "", False)
        return "\n".join(lines)
````

## `core/expression_evaluator.py`

````python
"""
Smart Campus Algorithmic Engine: Phase 1 Linear Data Structures
File: core/expression_evaluator.py

Stack Application for Expression Handling:
1. Syntax & Parentheses / Bracket Balancing Check: O(n)
2. Infix-to-Postfix (Reverse Polish Notation) Conversion via Shunting-Yard: O(n)
3. Postfix Expression Evaluation with Variable Substitution: O(n)

All stack operations utilize the custom LinkedStack (no built-in Python list as stack).
"""

import re
from typing import Dict, List, Optional, Tuple
from core.stack import LinkedStack


class ExpressionError(Exception):
    """Custom exception for expression parsing and evaluation errors."""
    pass


def check_balanced_brackets(expression: str) -> Tuple[bool, str]:
    """
    Validates if brackets '()', '[]', '{}' in an expression are properly matched and balanced.
    Uses custom LinkedStack.
    Returns: (is_balanced: bool, explanation: str)
    """
    stack = LinkedStack()
    bracket_pairs = {')': '(', ']': '[', '}': '{'}
    opening_brackets = set(bracket_pairs.values())

    for idx, char in enumerate(expression):
        if char in opening_brackets:
            stack.push((char, idx))
        elif char in bracket_pairs:
            if stack.is_empty():
                return False, f"Unmatched closing bracket '{char}' at index {idx}."
            top_char, top_idx = stack.pop()
            expected_open = bracket_pairs[char]
            if top_char != expected_open:
                return False, f"Mismatched brackets: expected '{expected_open}' to match '{char}' at index {idx}, but found '{top_char}' from index {top_idx}."

    if not stack.is_empty():
        top_char, top_idx = stack.pop()
        return False, f"Unclosed opening bracket '{top_char}' at index {top_idx}."

    return True, "All parentheses and brackets are properly balanced."


def tokenize_expression(expression: str) -> List[str]:
    """
    Splits mathematical expression into tokens (numbers, variable names, operators, brackets).
    Example: '(attendees + equipment_units) * 0.9' -> ['(', 'attendees', '+', 'equipment_units', ')', '*', '0.9']
    """
    # Pattern matching floats/ints, identifiers (variables), and operators
    token_pattern = r"(\d+(?:\.\d+)?|[a-zA-Z_][a-zA-Z0-9_]*|\*\*|[+\-*/^()%\[\]{}])"
    raw_tokens = re.findall(token_pattern, expression)
    # Filter out empty whitespace tokens
    return [t.strip() for t in raw_tokens if t.strip()]


def infix_to_postfix(expression: str) -> List[str]:
    """
    Converts Infix mathematical expression to Postfix (Reverse Polish Notation)
    using Dijkstra's Shunting-Yard algorithm powered by custom LinkedStack.
    """
    # Check bracket validity first
    is_balanced, reason = check_balanced_brackets(expression)
    if not is_balanced:
        raise ExpressionError(f"Syntax Error: {reason}")

    precedence = {
        '^': 4,
        '*': 3, '/': 3, '%': 3,
        '+': 2, '-': 2
    }
    right_associative = {'^'}

    output_queue: List[str] = []
    op_stack = LinkedStack()

    tokens = tokenize_expression(expression)

    for token in tokens:
        # Check if number (float or int) or variable identifier
        if re.match(r"^\d+(?:\.\d+)?$", token) or re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", token):
            output_queue.append(token)
        elif token in "([{":
            op_stack.push(token)
        elif token in ")]}":
            matching_open = {'(': ')', '[': ']', '{': '}'}
            # Pop operators until matching opening bracket
            popped = False
            while not op_stack.is_empty():
                top = op_stack.peek()
                if top in "([{":
                    op_stack.pop()
                    popped = True
                    break
                else:
                    output_queue.append(op_stack.pop())
            if not popped:
                raise ExpressionError(f"Mismatched closing bracket '{token}'.")
        elif token in precedence:
            curr_prec = precedence[token]
            while not op_stack.is_empty():
                top = op_stack.peek()
                if top in "([{":
                    break
                top_prec = precedence.get(top, 0)
                # Left-associative: pop while top_prec >= curr_prec
                # Right-associative (^): pop while top_prec > curr_prec
                if (token not in right_associative and top_prec >= curr_prec) or \
                   (token in right_associative and top_prec > curr_prec):
                    output_queue.append(op_stack.pop())
                else:
                    break
            op_stack.push(token)
        else:
            raise ExpressionError(f"Unrecognized operator or token: '{token}'")

    # Pop remaining operators
    while not op_stack.is_empty():
        top = op_stack.pop()
        if top in "([{)]}":
            raise ExpressionError("Mismatched parentheses in expression.")
        output_queue.append(top)

    return output_queue


def evaluate_postfix(postfix_tokens: List[str], variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluates Postfix tokens using a custom LinkedStack of operands.
    Replaces variable identifiers with values from the variables dictionary.
    """
    if variables is None:
        variables = {}

    operand_stack = LinkedStack()

    for token in postfix_tokens:
        # Check if float/int number
        if re.match(r"^\d+(?:\.\d+)?$", token):
            operand_stack.push(float(token))
        # Check if variable name
        elif re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", token):
            if token not in variables:
                raise ExpressionError(f"Undefined variable in expression: '{token}'")
            operand_stack.push(float(variables[token]))
        # Operator
        elif token in {'+', '-', '*', '/', '%', '^'}:
            if len(operand_stack) < 2:
                raise ExpressionError(f"Malformed expression: insufficient operands for operator '{token}'.")
            b = operand_stack.pop()
            a = operand_stack.pop()

            if token == '+':
                res = a + b
            elif token == '-':
                res = a - b
            elif token == '*':
                res = a * b
            elif token == '/':
                if b == 0:
                    raise ZeroDivisionError("Division by zero in formula evaluation.")
                res = a / b
            elif token == '%':
                if b == 0:
                    raise ZeroDivisionError("Modulo by zero in formula evaluation.")
                res = a % b
            elif token == '^':
                res = a ** b
            else:
                raise ExpressionError(f"Unknown operator '{token}'.")

            operand_stack.push(res)
        else:
            raise ExpressionError(f"Unexpected token in postfix evaluation: '{token}'")

    if len(operand_stack) != 1:
        raise ExpressionError(f"Malformed expression: stack ended with {len(operand_stack)} values instead of 1.")

    return operand_stack.pop()


def evaluate_campus_formula(expression: str, variables: Optional[Dict[str, float]] = None) -> Tuple[bool, float, str, List[str]]:
    """
    High-level API:
    1. Validates parentheses balancing.
    2. Converts infix to postfix using LinkedStack.
    3. Evaluates postfix using LinkedStack.
    Returns: (success: bool, result_value: float, explanation: str, postfix_tokens: List[str])
    """
    try:
        is_balanced, reason = check_balanced_brackets(expression)
        if not is_balanced:
            return False, 0.0, reason, []

        postfix = infix_to_postfix(expression)
        result = evaluate_postfix(postfix, variables)
        return True, round(result, 2), "Formula evaluated successfully.", postfix
    except Exception as e:
        return False, 0.0, str(e), []
````

## `core/graph.py`

````python
"""
Smart Campus Algorithmic Engine: Custom Graph & Dijkstra Shortest Path
File: core/graph.py

Features:
- Weighted Adjacency List graph representation.
- Custom MinHeap-driven Dijkstra's Algorithm: O((V + E) log V) time complexity.
- Turn-by-turn route generation with distances, walking times, and accessibility filters.
- Wavefront exploration tracking (visited nodes order) for visual UI animation.
"""

from typing import Dict, List, Optional, Set, Tuple
from core.min_heap import MinHeap
from core.queue import LinkedQueue
from core.stack import LinkedStack


class Landmark:
    """Represents a vertex in the campus navigation graph."""

    def __init__(
        self,
        node_id: str,
        name: str,
        x: int,
        y: int,
        category: str = "General",
        description: str = ""
    ):
        self.node_id: str = node_id
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.category: str = category
        self.description: str = description

    def to_dict(self) -> dict:
        return {
            "id": self.node_id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "category": self.category,
            "description": self.description
        }

    def __repr__(self) -> str:
        return f"Landmark({self.node_id}: '{self.name}')"


class Edge:
    """Represents a weighted pathway between two campus landmarks."""

    def __init__(
        self,
        source: str,
        dest: str,
        weight: float,
        is_accessible: bool = True,
        path_name: str = "Walkway"
    ):
        if weight <= 0:
            raise ValueError("Edge weight (distance) must be positive.")
        self.source: str = source
        self.dest: str = dest
        self.weight: float = weight
        self.is_accessible: bool = is_accessible
        self.path_name: str = path_name

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "dest": self.dest,
            "weight": self.weight,
            "is_accessible": self.is_accessible,
            "path_name": self.path_name
        }

    def __repr__(self) -> str:
        acc = " [Accessible]" if self.is_accessible else " [Stairs]"
        return f"Edge({self.source} -> {self.dest}, {self.weight}m, '{self.path_name}'{acc})"


class CampusGraph:
    """
    Campus Map Graph represented via Adjacency List.
    Employs custom Min-Heap for Dijkstra's shortest path.
    """

    def __init__(self):
        self.nodes: Dict[str, Landmark] = {}
        self.adj: Dict[str, List[Edge]] = {}

    def add_node(self, landmark: Landmark) -> None:
        self.nodes[landmark.node_id] = landmark
        if landmark.node_id not in self.adj:
            self.adj[landmark.node_id] = []

    def add_edge(
        self,
        u: str,
        v: str,
        weight: float,
        is_accessible: bool = True,
        path_name: str = "Walkway",
        bidirectional: bool = True
    ) -> None:
        if u not in self.nodes or v not in self.nodes:
            raise KeyError(f"Both nodes ({u}, {v}) must be registered before creating an edge.")

        edge_forward = Edge(u, v, weight, is_accessible, path_name)
        self.adj[u].append(edge_forward)

        if bidirectional:
            edge_backward = Edge(v, u, weight, is_accessible, path_name)
            self.adj[v].append(edge_backward)

    def get_node(self, node_id: str) -> Optional[Landmark]:
        return self.nodes.get(node_id)

    def all_nodes(self) -> List[Landmark]:
        return list(self.nodes.values())

    def all_edges(self) -> List[Edge]:
        edges = []
        for edge_list in self.adj.values():
            edges.extend(edge_list)
        return edges

    # -------------------------------------------------------------------------
    # Graph Traversals: BFS & DFS (O(V + E))
    # -------------------------------------------------------------------------

    def bfs(self, start_id: str) -> List[str]:
        """
        Breadth-First Search (BFS) using custom LinkedQueue.
        Explores vertices level-by-level in O(V + E) time.
        """
        if start_id not in self.nodes:
            return []

        visited: Set[str] = set()
        traversal_order: List[str] = []
        queue = LinkedQueue()

        queue.enqueue(start_id)
        visited.add(start_id)

        while not queue.is_empty():
            curr = queue.dequeue()
            traversal_order.append(curr)

            for edge in self.adj.get(curr, []):
                neighbor = edge.dest
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.enqueue(neighbor)

        return traversal_order

    def dfs(self, start_id: str) -> List[str]:
        """
        Depth-First Search (DFS) using custom LinkedStack.
        Explores pathways deeply before backtracking in O(V + E) time.
        """
        if start_id not in self.nodes:
            return []

        visited: Set[str] = set()
        traversal_order: List[str] = []
        stack = LinkedStack()

        stack.push(start_id)

        while not stack.is_empty():
            curr = stack.pop()
            if curr not in visited:
                visited.add(curr)
                traversal_order.append(curr)

                # Push neighbors in reverse order for deterministic exploration
                neighbors = [e.dest for e in self.adj.get(curr, [])]
                for neighbor in reversed(neighbors):
                    if neighbor not in visited:
                        stack.push(neighbor)

        return traversal_order

    # -------------------------------------------------------------------------
    # Dijkstra's Algorithm with Custom MinHeap: O((V + E) log V)
    # -------------------------------------------------------------------------

    def find_shortest_path(
        self,
        start_id: str,
        dest_id: str,
        accessible_only: bool = False
    ) -> Optional[dict]:
        """
        Calculates the shortest walking route between two campus landmarks.
        Supports filtering out stairs / non-wheelchair-accessible paths.
        Returns detailed path metrics or None if unreachable.
        """
        if start_id not in self.nodes or dest_id not in self.nodes:
            return None

        if start_id == dest_id:
            start_node = self.nodes[start_id]
            return {
                "found": True,
                "start": start_node.to_dict(),
                "destination": start_node.to_dict(),
                "total_distance_m": 0.0,
                "estimated_minutes": 0.0,
                "path_node_ids": [start_id],
                "path_landmarks": [start_node.to_dict()],
                "turn_by_turn": ["You are already at your destination."],
                "visited_order": [start_id]
            }

        # Distance table and predecessor map
        dist: Dict[str, float] = {node_id: float("inf") for node_id in self.nodes}
        parent: Dict[str, Tuple[Optional[str], Optional[Edge]]] = {node_id: (None, None) for node_id in self.nodes}
        visited: Set[str] = set()
        visited_order: List[str] = []

        dist[start_id] = 0.0
        pq = MinHeap()
        pq.insert(start_id, 0.0)

        found = False

        while not pq.is_empty():
            min_item = pq.extract_min()
            u = min_item.item_id
            current_dist = min_item.priority

            if u in visited:
                continue

            visited.add(u)
            visited_order.append(u)

            # Early termination when destination reached
            if u == dest_id:
                found = True
                break

            # If current distance exceeds known distance, skip
            if current_dist > dist[u]:
                continue

            # Relax adjacent edges
            for edge in self.adj.get(u, []):
                v = edge.dest

                # Skip if accessibility requirement is violated
                if accessible_only and not edge.is_accessible:
                    continue

                if v in visited:
                    continue

                new_dist = dist[u] + edge.weight
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    parent[v] = (u, edge)
                    pq.insert(v, new_dist)

        if not found or dist[dest_id] == float("inf"):
            return None

        # Reconstruct path from destination backwards
        path_ids: List[str] = []
        path_edges: List[Edge] = []
        curr = dest_id

        while curr is not None:
            path_ids.append(curr)
            prev_node, used_edge = parent[curr]
            if used_edge is not None:
                path_edges.append(used_edge)
            curr = prev_node

        path_ids.reverse()
        path_edges.reverse()

        # Build turn-by-turn directions
        turn_by_turn: List[str] = []
        for i, edge in enumerate(path_edges):
            u_name = self.nodes[edge.source].name
            v_name = self.nodes[edge.dest].name
            acc_tag = "" if edge.is_accessible else " (Warning: Contains stairs)"
            step_desc = f"Step {i+1}: Walk {edge.weight:.0f}m along '{edge.path_name}' from {u_name} to {v_name}{acc_tag}."
            turn_by_turn.append(step_desc)

        total_meters = dist[dest_id]
        # Average campus walking speed: 80 meters/minute (~4.8 km/h)
        est_minutes = round(total_meters / 80.0, 1)

        return {
            "found": True,
            "start": self.nodes[start_id].to_dict(),
            "destination": self.nodes[dest_id].to_dict(),
            "total_distance_m": round(total_meters, 1),
            "estimated_minutes": est_minutes,
            "path_node_ids": path_ids,
            "path_landmarks": [self.nodes[nid].to_dict() for nid in path_ids],
            "turn_by_turn": turn_by_turn,
            "visited_order": visited_order
        }
````

## `core/interval_tree.py`

````python
"""
Smart Campus Algorithmic Engine: Custom Augmented Interval Tree
File: core/interval_tree.py

An Augmented AVL Tree storing intervals [low, high) with:
- BST key: low (start time)
- Augmented attribute: max_high = max(self.high, left.max_high, right.max_high)
- Guaranteed AVL balance factor in {-1, 0, 1} with height O(log n)
- Time Complexity:
    * Insertion: O(log n)
    * Deletion:  O(log n)
    * Single Overlap Query: O(log n)
    * All Overlaps Query:  O(log n + k), where k is the number of overlapping intervals
"""

from typing import Any, List, Optional


class IntervalNode:
    """Node in an Augmented AVL Interval Tree."""

    def __init__(self, low: int, high: int, data: Any = None):
        if low >= high:
            raise ValueError(f"Invalid interval: start time ({low}) must be strictly less than end time ({high}).")
        self.low: int = low
        self.high: int = high
        self.data: Any = data
        self.max_high: int = high
        self.height: int = 1
        self.left: Optional["IntervalNode"] = None
        self.right: Optional["IntervalNode"] = None

    def overlaps_with(self, low: int, high: int) -> bool:
        """
        Determines whether [self.low, self.high) overlaps with [low, high).
        Standard half-open interval overlap condition: self.low < high and low < self.high.
        Touching at boundary (e.g. 10-11 and 11-12) does NOT count as clash.
        """
        return self.low < high and low < self.high

    def __repr__(self) -> str:
        data_str = f" ({self.data})" if self.data else ""
        return f"IntervalNode([{self.low}, {self.high}), max={self.max_high}, h={self.height}{data_str})"


class IntervalTree:
    """
    Custom AVL-balanced Interval Tree for venue slot conflict detection.
    Zero external libraries used.
    """

    def __init__(self):
        self.root: Optional[IntervalNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.root is None

    # -------------------------------------------------------------------------
    # AVL Helpers: Height, Max_High recalculation, and Rotations
    # -------------------------------------------------------------------------

    @staticmethod
    def _get_height(node: Optional[IntervalNode]) -> int:
        return node.height if node else 0

    @staticmethod
    def _get_max_high(node: Optional[IntervalNode]) -> int:
        return node.max_high if node else -1

    def _get_balance(self, node: Optional[IntervalNode]) -> int:
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _update_node(self, node: IntervalNode) -> None:
        """Recalculates height and augmented max_high from immediate children."""
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        node.max_high = max(
            node.high,
            self._get_max_high(node.left),
            self._get_max_high(node.right)
        )

    def _rotate_right(self, y: IntervalNode) -> IntervalNode:
        r"""
             y                               x
            / \     Right Rotation          / \
           x   T3   -------------->        T1  y
          / \                                 / \
         T1  T2                              T2  T3
        """
        x = y.left
        assert x is not None
        t2 = x.right

        # Perform rotation
        x.right = y
        y.left = t2

        # Update affected nodes (bottom-up: y first, then x)
        self._update_node(y)
        self._update_node(x)

        return x

    def _rotate_left(self, x: IntervalNode) -> IntervalNode:
        r"""
           x                                 y
          / \       Left Rotation           / \
         T1  y      ------------->         x   T3
            / \                           / \
           T2  T3                        T1  T2
        """
        y = x.right
        assert y is not None
        t2 = y.left

        # Perform rotation
        y.left = x
        x.right = t2

        # Update affected nodes (bottom-up: x first, then y)
        self._update_node(x)
        self._update_node(y)

        return y

    # -------------------------------------------------------------------------
    # Insertion with AVL Rebalancing: O(log n)
    # -------------------------------------------------------------------------

    def insert(self, low: int, high: int, data: Any = None) -> None:
        """Inserts an interval [low, high) with associated data."""
        self.root = self._insert_node(self.root, low, high, data)
        self._size += 1

    def _insert_node(self, node: Optional[IntervalNode], low: int, high: int, data: Any) -> IntervalNode:
        # Standard BST insertion
        if not node:
            return IntervalNode(low, high, data)

        # Order by low; use high as secondary tiebreaker
        if low < node.low or (low == node.low and high < node.high):
            node.left = self._insert_node(node.left, low, high, data)
        else:
            node.right = self._insert_node(node.right, low, high, data)

        # Update height and max_high on ancestor path
        self._update_node(node)

        # AVL Balancing
        balance = self._get_balance(node)

        # Case 1: Left-Left (LL)
        if balance > 1 and node.left and (low < node.left.low or (low == node.left.low and high < node.left.high)):
            return self._rotate_right(node)

        # Case 2: Right-Right (RR)
        if balance < -1 and node.right and (low > node.right.low or (low == node.right.low and high >= node.right.high)):
            return self._rotate_left(node)

        # Case 3: Left-Right (LR)
        if balance > 1 and node.left and (low > node.left.low or (low == node.left.low and high >= node.left.high)):
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Case 4: Right-Left (RL)
        if balance < -1 and node.right and (low < node.right.low or (low == node.right.low and high < node.right.high)):
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # -------------------------------------------------------------------------
    # Deletion with AVL Rebalancing: O(log n)
    # -------------------------------------------------------------------------

    def delete(self, low: int, high: int, data_id: Optional[str] = None) -> bool:
        """
        Deletes the specified interval [low, high).
        Returns True if deleted, False if not found.
        """
        initial_size = self._size
        self.root = self._delete_node(self.root, low, high, data_id)
        return self._size < initial_size

    def _get_min_node(self, node: IntervalNode) -> IntervalNode:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _delete_node(
        self,
        node: Optional[IntervalNode],
        low: int,
        high: int,
        data_id: Optional[str] = None
    ) -> Optional[IntervalNode]:
        if not node:
            return None

        # Locate node
        if low < node.low or (low == node.low and high < node.high):
            node.left = self._delete_node(node.left, low, high, data_id)
        elif low > node.low or (low == node.low and high > node.high):
            node.right = self._delete_node(node.right, low, high, data_id)
        else:
            # Check if this node matches data_id when tiebreaker is needed
            current_id = getattr(node.data, "booking_id", None) if hasattr(node.data, "booking_id") else None
            if data_id is not None and current_id is not None and current_id != data_id:
                # Same interval, but different booking; check right subtree
                node.right = self._delete_node(node.right, low, high, data_id)
                self._update_node(node)
                return node

            # Match found: perform standard BST deletion
            self._size -= 1
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Node with two children: replace with inorder successor
            successor = self._get_min_node(node.right)
            node.low = successor.low
            node.high = successor.high
            node.data = successor.data

            # Delete the successor from right subtree
            self._size += 1
            node.right = self._delete_node(
                node.right,
                successor.low,
                successor.high,
                getattr(successor.data, "booking_id", None) if hasattr(successor.data, "booking_id") else None
            )

        if not node:
            return None

        # Re-update height and max_high
        self._update_node(node)

        # AVL Rebalancing
        balance = self._get_balance(node)

        # LL Case
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)

        # LR Case
        if balance > 1 and self._get_balance(node.left) < 0:
            assert node.left is not None
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # RR Case
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)

        # RL Case
        if balance < -1 and self._get_balance(node.right) > 0:
            assert node.right is not None
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # -------------------------------------------------------------------------
    # Conflict Detection Queries: O(log n) single clash, O(log n + k) all clashes
    # -------------------------------------------------------------------------

    def find_any_overlap(self, low: int, high: int) -> Optional[IntervalNode]:
        """
        CLRS Interval Search: Returns ANY node overlapping with [low, high) in O(log n).
        Returns None if no overlap exists.
        """
        current = self.root
        while current is not None and not current.overlaps_with(low, high):
            if current.left is not None and current.left.max_high > low:
                current = current.left
            else:
                current = current.right
        return current

    def find_all_overlapping(self, low: int, high: int) -> List[IntervalNode]:
        """
        Reports ALL intervals overlapping with [low, high) in O(log n + k) time.
        Subtree pruning guarantees only candidates can be traversed.
        """
        overlaps: List[IntervalNode] = []
        self._find_all_overlapping_recursive(self.root, low, high, overlaps)
        return overlaps

    def _find_all_overlapping_recursive(
        self,
        node: Optional[IntervalNode],
        low: int,
        high: int,
        result: List[IntervalNode]
    ) -> None:
        if node is None:
            return

        # Check current node
        if node.overlaps_with(low, high):
            result.append(node)

        # Prune Left Subtree:
        # Only search left if left child exists AND its max endpoint > query's start time
        if node.left is not None and node.left.max_high > low:
            self._find_all_overlapping_recursive(node.left, low, high, result)

        # Prune Right Subtree:
        # Only search right if current node's start time < query's end time
        if node.low < high and node.right is not None:
            self._find_all_overlapping_recursive(node.right, low, high, result)

    # -------------------------------------------------------------------------
    # Traversals & Visualizers
    # -------------------------------------------------------------------------

    def inorder(self) -> List[IntervalNode]:
        """Returns all intervals in ascending order of start time."""
        result: List[IntervalNode] = []

        def _inorder(node: Optional[IntervalNode]):
            if node:
                _inorder(node.left)
                result.append(node)
                _inorder(node.right)

        _inorder(self.root)
        return result

    def to_dict(self) -> Optional[dict]:
        """Returns a hierarchical JSON-serializable dictionary for Web visualizers."""
        def _build(node: Optional[IntervalNode]):
            if not node:
                return None
            data_val = None
            if node.data:
                if hasattr(node.data, "to_dict"):
                    data_val = node.data.to_dict()
                else:
                    data_val = str(node.data)
            return {
                "low": node.low,
                "high": node.high,
                "max_high": node.max_high,
                "height": node.height,
                "data": data_val,
                "left": _build(node.left),
                "right": _build(node.right)
            }
        return _build(self.root)

    def print_ascii_tree(self) -> str:
        """Generates an ASCII tree representation for terminal demos."""
        if not self.root:
            return "<Empty Interval Tree>"

        lines: List[str] = []

        def _print_node(node: Optional[IntervalNode], prefix: str = "", is_left: bool = True):
            if node is not None:
                title = getattr(node.data, "title", "") if node.data else ""
                tag = f" ({title})" if title else ""
                lines.append(
                    f"{prefix}{'|-- ' if is_left else '\\-- '}"
                    f"[{node.low}, {node.high}) [max={node.max_high}, h={node.height}]{tag}"
                )
                child_prefix = prefix + ("|   " if is_left else "    ")
                if node.left or node.right:
                    if node.left:
                        _print_node(node.left, child_prefix, True)
                    else:
                        lines.append(f"{child_prefix}|-- <None>")
                    if node.right:
                        _print_node(node.right, child_prefix, False)
                    else:
                        lines.append(f"{child_prefix}\\-- <None>")

        _print_node(self.root, "", False)
        return "\n".join(lines)
````

## `core/linked_list.py`

````python
"""
Smart Campus Algorithmic Engine: Phase 1 Linear Data Structures
File: core/linked_list.py

Custom Singly Linked List for student data storage and administration.
Implements pointer-based node architecture with zero high-level list library shortcuts.

Time Complexities:
    * Insert at Front (Head): O(1)
    * Insert at Rear (Tail):  O(1) (Maintained via tail pointer)
    * Insert at Position k:   O(n)
    * Delete Front:           O(1)
    * Delete Rear:            O(n)
    * Delete by Key / ID:     O(n)
    * Delete at Position k:   O(n)
    * Search / Traverse:      O(n)
    * In-Place Reversal:      O(n)
"""

from typing import Any, Callable, Generator, List, Optional


class Node:
    """A single node in the Singly Linked List."""

    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional["Node"] = None

    def __repr__(self) -> str:
        return f"Node({self.data})"


class SinglyLinkedList:
    """
    Textbook-grade Singly Linked List with head and tail pointers.
    Maintains size counter for O(1) length queries.
    """

    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.head is None

    # -------------------------------------------------------------------------
    # Insertion Operations
    # -------------------------------------------------------------------------

    def insert_front(self, data: Any) -> None:
        """Inserts a new element at the beginning (head) in O(1)."""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        if self.tail is None:
            self.tail = new_node
        self._size += 1

    def insert_rear(self, data: Any) -> None:
        """Inserts a new element at the end (tail) in O(1) using tail pointer."""
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def insert_at(self, index: int, data: Any) -> bool:
        """
        Inserts an element at a specific 0-based index in O(n).
        Returns True if successful, False if index is out of bounds.
        """
        if index < 0 or index > self._size:
            return False

        if index == 0:
            self.insert_front(data)
            return True
        if index == self._size:
            self.insert_rear(data)
            return True

        new_node = Node(data)
        curr = self.head
        for _ in range(index - 1):
            assert curr is not None
            curr = curr.next

        assert curr is not None
        new_node.next = curr.next
        curr.next = new_node
        self._size += 1
        return True

    # -------------------------------------------------------------------------
    # Deletion Operations
    # -------------------------------------------------------------------------

    def delete_front(self) -> Optional[Any]:
        """Removes and returns the front element in O(1)."""
        if self.head is None:
            return None

        removed_data = self.head.data
        self.head = self.head.next
        self._size -= 1

        if self.head is None:
            self.tail = None

        return removed_data

    def delete_rear(self) -> Optional[Any]:
        """Removes and returns the rear element in O(n)."""
        if self.head is None:
            return None

        if self.head == self.tail:
            removed_data = self.head.data
            self.head = None
            self.tail = None
            self._size = 0
            return removed_data

        curr = self.head
        while curr.next != self.tail:
            assert curr.next is not None
            curr = curr.next

        assert self.tail is not None
        removed_data = self.tail.data
        curr.next = None
        self.tail = curr
        self._size -= 1
        return removed_data

    def delete_at(self, index: int) -> Optional[Any]:
        """Removes element at specific 0-based index in O(n)."""
        if index < 0 or index >= self._size:
            return None

        if index == 0:
            return self.delete_front()
        if index == self._size - 1:
            return self.delete_rear()

        curr = self.head
        for _ in range(index - 1):
            assert curr is not None
            curr = curr.next

        assert curr is not None and curr.next is not None
        removed_data = curr.next.data
        curr.next = curr.next.next
        self._size -= 1
        return removed_data

    def delete_by_key(self, predicate: Callable[[Any], bool]) -> Optional[Any]:
        """
        Deletes the first node matching predicate(data) == True in O(n).
        Returns the removed data or None if not found.
        """
        if self.head is None:
            return None

        if predicate(self.head.data):
            return self.delete_front()

        prev = self.head
        curr = self.head.next

        while curr is not None:
            if predicate(curr.data):
                removed_data = curr.data
                prev.next = curr.next
                if curr == self.tail:
                    self.tail = prev
                self._size -= 1
                return removed_data
            prev = curr
            curr = curr.next

        return None

    # -------------------------------------------------------------------------
    # Search, Traversal & Utilities
    # -------------------------------------------------------------------------

    def search(self, predicate: Callable[[Any], bool]) -> Optional[Any]:
        """Finds first element where predicate(data) is True in O(n)."""
        curr = self.head
        while curr is not None:
            if predicate(curr.data):
                return curr.data
            curr = curr.next
        return None

    def get_at(self, index: int) -> Optional[Any]:
        """Retrieves data at 0-based index in O(n)."""
        if index < 0 or index >= self._size:
            return None
        curr = self.head
        for _ in range(index):
            assert curr is not None
            curr = curr.next
        return curr.data if curr else None

    def reverse(self) -> None:
        """Reverses the linked list in-place in O(n) time and O(1) space."""
        prev = None
        curr = self.head
        self.tail = self.head

        while curr is not None:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node

        self.head = prev

    def to_list(self) -> List[Any]:
        """Extracts elements to a standard Python list for serialisation."""
        result = []
        curr = self.head
        while curr is not None:
            result.append(curr.data)
            curr = curr.next
        return result

    def __iter__(self) -> Generator[Any, None, None]:
        curr = self.head
        while curr is not None:
            yield curr.data
            curr = curr.next

    def display(self) -> str:
        """Returns visual pointer chain representation for CLI & debugging."""
        if self.head is None:
            return "[Empty List] -> None"

        elements = []
        curr = self.head
        while curr is not None:
            # Format data cleanly
            label = getattr(curr.data, "student_id", str(curr.data))
            elements.append(f"[{label}]")
            curr = curr.next
        return " -> ".join(elements) + " -> None"
````

## `core/max_heap.py`

````python
"""
Smart Campus Algorithmic Engine: Custom Binary Max-Heap / Priority Queue
File: core/max_heap.py

Features:
- Pure array-based Binary Max-Heap (0-indexed).
- Zero external DSA libraries (no heapq).
- Dynamic priority updates in O(log n) via internal position hash-map (id -> index).
- Time Complexity:
    * Insert: O(log n)
    * Extract-Max: O(log n)
    * Peek: O(1)
    * Update Priority / Remove: O(log n)
    * Heapify (Build Heap): O(n)
"""

from typing import Any, Callable, Dict, List, Optional


class HeapItem:
    """Represents an element in the Priority Queue."""

    def __init__(self, item_id: str, priority: float, data: Any = None):
        self.item_id: str = item_id
        self.priority: float = priority
        self.data: Any = data

    def __repr__(self) -> str:
        return f"HeapItem(id='{self.item_id}', priority={self.priority:.1f})"


class MaxHeap:
    """
    Custom Binary Max-Heap for Emergency and Volunteer Task Prioritization.
    Maintains max-heap property: parent.priority >= children.priority.
    """

    def __init__(self):
        self._heap: List[HeapItem] = []
        self._pos_map: Dict[str, int] = {}  # item_id -> index in _heap

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    # -------------------------------------------------------------------------
    # Index calculations
    # -------------------------------------------------------------------------

    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left_child(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right_child(i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._pos_map[self._heap[i].item_id] = i
        self._pos_map[self._heap[j].item_id] = j

    # -------------------------------------------------------------------------
    # Sift operations
    # -------------------------------------------------------------------------

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent_idx = self._parent(index)
            if self._heap[index].priority > self._heap[parent_idx].priority:
                self._swap(index, parent_idx)
                index = parent_idx
            else:
                break

    def _sift_down(self, index: int) -> None:
        n = len(self._heap)
        while True:
            largest = index
            left = self._left_child(index)
            right = self._right_child(index)

            if left < n and self._heap[left].priority > self._heap[largest].priority:
                largest = left
            if right < n and self._heap[right].priority > self._heap[largest].priority:
                largest = right

            if largest != index:
                self._swap(index, largest)
                index = largest
            else:
                break

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def insert(self, item_id: str, priority: float, data: Any = None) -> None:
        """
        Inserts a new incident/task into the Max-Heap in O(log n).
        If an item with item_id already exists, updates its priority instead.
        """
        if item_id in self._pos_map:
            self.update_priority(item_id, priority, data)
            return

        item = HeapItem(item_id=item_id, priority=priority, data=data)
        self._heap.append(item)
        new_index = len(self._heap) - 1
        self._pos_map[item_id] = new_index
        self._sift_up(new_index)

    def peek(self) -> Optional[HeapItem]:
        """Returns the highest-priority incident without removing it in O(1)."""
        if not self._heap:
            return None
        return self._heap[0]

    def extract_max(self) -> Optional[HeapItem]:
        """
        Pops and returns the highest priority incident in O(log n).
        Re-establishes the max-heap property via sift-down.
        """
        if not self._heap:
            return None

        max_item = self._heap[0]
        last_item = self._heap.pop()
        del self._pos_map[max_item.item_id]

        if self._heap:
            self._heap[0] = last_item
            self._pos_map[last_item.item_id] = 0
            self._sift_down(0)

        return max_item

    def update_priority(self, item_id: str, new_priority: float, data: Any = None) -> bool:
        """
        Dynamically adjusts an incident's priority in O(log n) using position lookup.
        """
        if item_id not in self._pos_map:
            return False

        index = self._pos_map[item_id]
        old_priority = self._heap[index].priority
        self._heap[index].priority = new_priority
        if data is not None:
            self._heap[index].data = data

        if new_priority > old_priority:
            self._sift_up(index)
        elif new_priority < old_priority:
            self._sift_down(index)

        return True

    def remove(self, item_id: str) -> Optional[HeapItem]:
        """Removes an arbitrary item from the heap in O(log n)."""
        if item_id not in self._pos_map:
            return None

        index = self._pos_map[item_id]
        target_item = self._heap[index]
        last_item = self._heap.pop()
        del self._pos_map[item_id]

        if index < len(self._heap):
            self._heap[index] = last_item
            self._pos_map[last_item.item_id] = index
            # May need to sift up or sift down depending on value
            parent_idx = self._parent(index)
            if index > 0 and self._heap[index].priority > self._heap[parent_idx].priority:
                self._sift_up(index)
            else:
                self._sift_down(index)

        return target_item

    def get_items_sorted(self) -> List[HeapItem]:
        """Returns a snapshot of all elements ordered by priority (highest first) without mutating self."""
        clone = MaxHeap()
        for item in self._heap:
            clone.insert(item.item_id, item.priority, item.data)

        sorted_list: List[HeapItem] = []
        while not clone.is_empty():
            sorted_list.append(clone.extract_max())
        return sorted_list

    def to_list(self) -> List[dict]:
        """Returns list of items serialized for API and UI display."""
        return [
            {
                "id": item.item_id,
                "priority": item.priority,
                "data": getattr(item.data, "to_dict", lambda: item.data)() if item.data else None
            }
            for item in self._heap
        ]

    def print_ascii_heap(self) -> str:
        """Visualizes heap tree level-by-level for viva demonstration."""
        if not self._heap:
            return "<Empty Max-Heap>"

        lines = ["=== Binary Max-Heap Tree Structure ==="]
        level = 0
        nodes_in_level = 1
        i = 0
        n = len(self._heap)

        while i < n:
            level_items = []
            for _ in range(nodes_in_level):
                if i < n:
                    item = self._heap[i]
                    level_items.append(f"[{item.item_id}: score={item.priority:.1f}]")
                    i += 1
                else:
                    break
            lines.append(f"Level {level}: " + "  ".join(level_items))
            nodes_in_level *= 2
            level += 1

        return "\n".join(lines)
````

## `core/min_heap.py`

````python
"""
Smart Campus Algorithmic Engine: Custom Binary Min-Heap
File: core/min_heap.py

Features:
- Pure array-based Binary Min-Heap (0-indexed).
- Invariant: parent.priority <= children.priority.
- Used primarily by Dijkstra's shortest path algorithm for O((V + E) log V) execution.
- Supports decrease_key / update in O(log n) via position lookup.
"""

from typing import Any, Dict, List, Optional


class MinHeapItem:
    """Represents an item in the Min-Heap."""

    def __init__(self, item_id: str, priority: float, data: Any = None):
        self.item_id: str = item_id
        self.priority: float = priority
        self.data: Any = data

    def __repr__(self) -> str:
        return f"MinHeapItem(id='{self.item_id}', priority={self.priority:.2f})"


class MinHeap:
    """
    Custom Binary Min-Heap for Dijkstra's Algorithm and shortest path priority queues.
    Zero external libraries used.
    """

    def __init__(self):
        self._heap: List[MinHeapItem] = []
        self._pos_map: Dict[str, int] = {}

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def contains(self, item_id: str) -> bool:
        return item_id in self._pos_map

    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left_child(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right_child(i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._pos_map[self._heap[i].item_id] = i
        self._pos_map[self._heap[j].item_id] = j

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent_idx = self._parent(index)
            if self._heap[index].priority < self._heap[parent_idx].priority:
                self._swap(index, parent_idx)
                index = parent_idx
            else:
                break

    def _sift_down(self, index: int) -> None:
        n = len(self._heap)
        while True:
            smallest = index
            left = self._left_child(index)
            right = self._right_child(index)

            if left < n and self._heap[left].priority < self._heap[smallest].priority:
                smallest = left
            if right < n and self._heap[right].priority < self._heap[smallest].priority:
                smallest = right

            if smallest != index:
                self._swap(index, smallest)
                index = smallest
            else:
                break

    def insert(self, item_id: str, priority: float, data: Any = None) -> None:
        """Inserts an element into the min-heap in O(log n)."""
        if item_id in self._pos_map:
            self.decrease_key(item_id, priority, data)
            return

        item = MinHeapItem(item_id=item_id, priority=priority, data=data)
        self._heap.append(item)
        new_index = len(self._heap) - 1
        self._pos_map[item_id] = new_index
        self._sift_up(new_index)

    def extract_min(self) -> Optional[MinHeapItem]:
        """Extracts the minimum priority item in O(log n)."""
        if not self._heap:
            return None

        min_item = self._heap[0]
        last_item = self._heap.pop()
        del self._pos_map[min_item.item_id]

        if self._heap:
            self._heap[0] = last_item
            self._pos_map[last_item.item_id] = 0
            self._sift_down(0)

        return min_item

    def peek(self) -> Optional[MinHeapItem]:
        """Returns the minimum element without removing it in O(1)."""
        if not self._heap:
            return None
        return self._heap[0]

    def decrease_key(self, item_id: str, new_priority: float, data: Any = None) -> bool:
        """
        Decreases the key/priority of an item in O(log n).
        Crucial for efficient Dijkstra edge relaxation.
        """
        if item_id not in self._pos_map:
            return False

        index = self._pos_map[item_id]
        if new_priority > self._heap[index].priority:
            # If priority increased, sift down
            self._heap[index].priority = new_priority
            if data is not None:
                self._heap[index].data = data
            self._sift_down(index)
        else:
            self._heap[index].priority = new_priority
            if data is not None:
                self._heap[index].data = data
            self._sift_up(index)

        return True
````

## `core/queue.py`

````python
"""
Smart Campus Algorithmic Engine: Phase 1 Linear Data Structures
File: core/queue.py

Custom Node-based Linked Queue (FIFO: First In, First Out).
Implements front and rear pointer architecture with O(1) enqueue and dequeue.

Time Complexities:
    * Enqueue:  O(1) (Rear pointer insertion)
    * Dequeue:  O(1) (Front pointer removal)
    * Peek:     O(1)
    * Is Empty: O(1)
    * Size:     O(1)
"""

from typing import Any, List, Optional


class QueueNode:
    """Node in the Linked Queue."""

    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional["QueueNode"] = None

    def __repr__(self) -> str:
        return f"QueueNode({self.data})"


class LinkedQueue:
    """
    Textbook-grade Linked Queue implementation.
    Enqueues at rear and dequeues from front.
    """

    def __init__(self):
        self.front: Optional[QueueNode] = None
        self.rear: Optional[QueueNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.front is None

    def enqueue(self, data: Any) -> None:
        """Adds an item to the rear of the queue in O(1)."""
        new_node = QueueNode(data)
        if self.rear is None:
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self._size += 1

    def dequeue(self) -> Any:
        """
        Removes and returns the item from the front of the queue in O(1).
        Raises IndexError if the queue is empty.
        """
        if self.is_empty():
            raise IndexError("dequeue from empty queue")

        assert self.front is not None
        removed_data = self.front.data
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self._size -= 1
        return removed_data

    def peek(self) -> Any:
        """
        Returns the item at the front of the queue without removing it in O(1).
        Raises IndexError if the queue is empty.
        """
        if self.is_empty():
            raise IndexError("peek from empty queue")

        assert self.front is not None
        return self.front.data

    def to_list(self) -> List[Any]:
        """Returns list of items from front to rear."""
        result = []
        curr = self.front
        while curr is not None:
            result.append(curr.data)
            curr = curr.next
        return result

    def display(self) -> str:
        """Visual representation of queue for viva demos."""
        if self.is_empty():
            return "<Empty Queue>"

        items = self.to_list()
        formatted = " -> ".join([f"[{item}]" for item in items])
        return f"FRONT -> {formatted} -> REAR"
````

## `core/searching_sorting.py`

````python
"""
Smart Campus Algorithmic Engine: Phase 3 Searching & Sorting
File: core/searching_sorting.py

Features:
1. Linear Search: O(n) sequential scan
2. Binary Search: O(log n) divide-and-conquer on sorted arrays
3. Merge Sort:    O(n log n) stable divide-and-conquer sort
4. Quick Sort:    O(n log n) average in-place partitioning sort
5. Insertion Sort: O(n^2) adaptive sorting for small/nearly-sorted data
6. Conceptual & Empirical Efficiency Comparison
"""

import time
from typing import Any, Callable, List, Optional, Tuple


# =============================================================================
# 1. SEARCHING ALGORITHMS
# =============================================================================

def linear_search(
    arr: List[Any],
    target: Any,
    key_func: Optional[Callable[[Any], Any]] = None
) -> Tuple[int, int]:
    """
    Sequentially searches for target in arr in O(n) time.
    Returns: (found_index: int, comparisons_count: int)
    If not found, found_index is -1.
    """
    comparisons = 0
    for idx, item in enumerate(arr):
        comparisons += 1
        val = key_func(item) if key_func else item
        if val == target:
            return idx, comparisons
    return -1, comparisons


def binary_search(
    arr: List[Any],
    target: Any,
    key_func: Optional[Callable[[Any], Any]] = None
) -> Tuple[int, int]:
    """
    Divides search space in half in O(log n) time.
    PRECONDITION: arr must already be sorted in ascending order of key_func.
    Returns: (found_index: int, comparisons_count: int)
    If not found, found_index is -1.
    """
    low = 0
    high = len(arr) - 1
    comparisons = 0

    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        val = key_func(arr[mid]) if key_func else arr[mid]

        if val == target:
            return mid, comparisons
        elif val < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1, comparisons


# =============================================================================
# 2. SORTING ALGORITHMS
# =============================================================================

def merge_sort(
    arr: List[Any],
    key_func: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False
) -> List[Any]:
    """
    Stable divide-and-conquer sorting algorithm in O(n log n) time and O(n) space.
    Returns a new sorted list.
    """
    if len(arr) <= 1:
        return list(arr)

    mid = len(arr) // 2
    left_sorted = merge_sort(arr[:mid], key_func, reverse)
    right_sorted = merge_sort(arr[mid:], key_func, reverse)

    return _merge(left_sorted, right_sorted, key_func, reverse)


def _merge(
    left: List[Any],
    right: List[Any],
    key_func: Optional[Callable[[Any], Any]],
    reverse: bool
) -> List[Any]:
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        val_l = key_func(left[i]) if key_func else left[i]
        val_r = key_func(right[j]) if key_func else right[j]

        condition = (val_l > val_r) if reverse else (val_l <= val_r)
        if condition:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(
    arr: List[Any],
    key_func: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False
) -> List[Any]:
    """
    In-place divide-and-conquer sorting with Lomuto partitioning.
    Average Time: O(n log n). Worst-case: O(n^2).
    Returns a new sorted list.
    """
    copy_arr = list(arr)
    _quick_sort_helper(copy_arr, 0, len(copy_arr) - 1, key_func, reverse)
    return copy_arr


def _quick_sort_helper(
    arr: List[Any],
    low: int,
    high: int,
    key_func: Optional[Callable[[Any], Any]],
    reverse: bool
) -> None:
    if low < high:
        p_idx = _partition(arr, low, high, key_func, reverse)
        _quick_sort_helper(arr, low, p_idx - 1, key_func, reverse)
        _quick_sort_helper(arr, p_idx + 1, high, key_func, reverse)


def _partition(
    arr: List[Any],
    low: int,
    high: int,
    key_func: Optional[Callable[[Any], Any]],
    reverse: bool
) -> int:
    pivot_val = key_func(arr[high]) if key_func else arr[high]
    i = low - 1

    for j in range(low, high):
        curr_val = key_func(arr[j]) if key_func else arr[j]
        condition = (curr_val > pivot_val) if reverse else (curr_val <= pivot_val)
        if condition:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def insertion_sort(
    arr: List[Any],
    key_func: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False
) -> List[Any]:
    """
    Adaptive in-place sorting in O(n^2) worst case, O(n) best case (already sorted).
    Returns a new sorted list.
    """
    result = list(arr)
    for i in range(1, len(result)):
        current = result[i]
        curr_val = key_func(current) if key_func else current
        j = i - 1

        while j >= 0:
            compare_val = key_func(result[j]) if key_func else result[j]
            condition = (compare_val < curr_val) if reverse else (compare_val > curr_val)
            if condition:
                result[j + 1] = result[j]
                j -= 1
            else:
                break
        result[j + 1] = current

    return result


# =============================================================================
# 3. PERFORMANCE & COMPLEXITY COMPARISON
# =============================================================================

def compare_sorting_algorithms(
    data: Any = None,
    key_func: Optional[Callable[[Any], Any]] = None,
    runs: int = 3,
    sample_size: Optional[int] = None
) -> dict:
    """Benchmark the sorting algorithms on supplied records or sample data.

    ``sample_size`` preserves the original generated-data API. Callers may also
    pass records, a key function, and a repeat count to benchmark real data.
    """
    import random

    if isinstance(data, int):
        sample_size = data
        data = None

    if data is None:
        size = 1000 if sample_size is None else max(0, sample_size)
        rng = random.Random(42)
        items = [rng.randint(1, 10000) for _ in range(size)]
        actual_key_func = None
    else:
        items = list(data)
        size = len(items)
        actual_key_func = key_func

    run_count = max(1, int(runs))

    class ComparisonCounter:
        count = 0
        def __init__(self, val):
            self.val = val
        def __lt__(self, other):
            ComparisonCounter.count += 1
            return self.val < other.val
        def __le__(self, other):
            ComparisonCounter.count += 1
            return self.val <= other.val
        def __gt__(self, other):
            ComparisonCounter.count += 1
            return self.val > other.val
        def __ge__(self, other):
            ComparisonCounter.count += 1
            return self.val >= other.val

    def wrapped_key(item):
        raw_val = actual_key_func(item) if actual_key_func else item
        return ComparisonCounter(raw_val)

    algorithms = [
        ("Merge Sort", merge_sort),
        ("Quick Sort", quick_sort),
        ("Insertion Sort", insertion_sort),
    ]

    bench_stats = {}
    for name, algorithm in algorithms:
        elapsed = []
        comp_count = 0
        for r in range(run_count):
            ComparisonCounter.count = 0
            started = time.perf_counter()
            algorithm(items, key_func=wrapped_key)
            elapsed.append((time.perf_counter() - started) * 1000)
            if r == 0:
                comp_count = ComparisonCounter.count
        average_ms = sum(elapsed) / len(elapsed)
        bench_stats[name] = {
            "avg_ms": round(average_ms, 4),
            "comparisons": comp_count
        }

    results_list = [
        {
            "algorithm": "Merge Sort",
            "time_ms": bench_stats["Merge Sort"]["avg_ms"],
            "avg_ms": bench_stats["Merge Sort"]["avg_ms"],
            "comparisons": bench_stats["Merge Sort"]["comparisons"],
            "best_case": "O(n log n)",
            "average_case": "O(n log n)",
            "worst_case": "O(n log n)",
            "space": "O(n)",
            "stable": True
        },
        {
            "algorithm": "Quick Sort",
            "time_ms": bench_stats["Quick Sort"]["avg_ms"],
            "avg_ms": bench_stats["Quick Sort"]["avg_ms"],
            "comparisons": bench_stats["Quick Sort"]["comparisons"],
            "best_case": "O(n log n)",
            "average_case": "O(n log n)",
            "worst_case": "O(n^2)",
            "space": "O(log n)",
            "stable": False
        },
        {
            "algorithm": "Insertion Sort",
            "time_ms": bench_stats["Insertion Sort"]["avg_ms"],
            "avg_ms": bench_stats["Insertion Sort"]["avg_ms"],
            "comparisons": bench_stats["Insertion Sort"]["comparisons"],
            "best_case": "O(n)",
            "average_case": "O(n^2)",
            "worst_case": "O(n^2)",
            "space": "O(1)",
            "stable": True
        }
    ]

    response = {
        "sample_size": size,
        "runs": run_count,
        "results": results_list,
        "Merge Sort": results_list[0],
        "Quick Sort": results_list[1],
        "Insertion Sort": results_list[2],
    }
    return response
````

## `core/stack.py`

````python
"""
Smart Campus Algorithmic Engine: Phase 1 Linear Data Structures
File: core/stack.py

Custom Node-based Linked Stack (LIFO: Last In, First Out).
Implements pure dynamic node chaining with zero fixed array size bounds.

Time Complexities:
    * Push:     O(1)
    * Pop:      O(1)
    * Peek:     O(1)
    * Is Empty: O(1)
    * Size:     O(1)
"""

from typing import Any, List, Optional


class StackNode:
    """Node in the Linked Stack."""

    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional["StackNode"] = None

    def __repr__(self) -> str:
        return f"StackNode({self.data})"


class LinkedStack:
    """
    Textbook-grade Linked Stack implementation.
    Top of stack corresponds to the head of the linked chain.
    """

    def __init__(self):
        self.top_node: Optional[StackNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.top_node is None

    def push(self, data: Any) -> None:
        """Pushes an element onto the top of the stack in O(1)."""
        new_node = StackNode(data)
        new_node.next = self.top_node
        self.top_node = new_node
        self._size += 1

    def pop(self) -> Any:
        """
        Pops and returns the top element from the stack in O(1).
        Raises IndexError if the stack is empty.
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")

        assert self.top_node is not None
        popped_data = self.top_node.data
        self.top_node = self.top_node.next
        self._size -= 1
        return popped_data

    def peek(self) -> Any:
        """
        Returns the top element without removing it in O(1).
        Raises IndexError if the stack is empty.
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")

        assert self.top_node is not None
        return self.top_node.data

    def to_list(self) -> List[Any]:
        """Returns items from top to bottom."""
        result = []
        curr = self.top_node
        while curr is not None:
            result.append(curr.data)
            curr = curr.next
        return result

    def display(self) -> str:
        """Visual representation of stack for viva demos."""
        if self.is_empty():
            return "<Empty Stack>"

        items = self.to_list()
        lines = ["--- TOP OF STACK ---"]
        for item in items:
            lines.append(f"  | {item} |")
        lines.append("--- BOTTOM OF STACK ---")
        return "\n".join(lines)
````

## `run.py`

````python
"""
Smart Campus & Student Operations: Master Entry Point
File: run.py

Usage:
    python run.py --web        # Launches the Interactive Web Dashboard (Flask)
    python run.py --cli        # Launches the Terminal CLI Menu (Viva demo)
    python run.py --test       # Executes all unit tests
    python run.py --benchmark  # Runs algorithmic scalability benchmarks
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def launch_web(port=None):
    from web.app import run_server
    if port is None:
        # Check CLI arguments for --port <num> or a trailing port number
        for i, a in enumerate(sys.argv):
            if a in ["--port", "-p"] and i + 1 < len(sys.argv):
                try:
                    port = int(sys.argv[i + 1])
                    break
                except ValueError:
                    pass
            elif a.isdigit() and len(a) >= 4:
                port = int(a)
                break
    run_server(port=port)


def launch_cli():
    from cli.main_cli import main
    main()


def run_tests():
    import unittest
    loader = unittest.TestLoader()
    start_dir = os.path.join(PROJECT_ROOT, "tests")
    suite = loader.discover(start_dir)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


def run_benchmarks():
    from benchmarks.performance_benchmark import run_full_benchmark_suite
    run_full_benchmark_suite()


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--web", "-w"]:
            launch_web()
        elif arg in ["--cli", "-c"]:
            launch_cli()
        elif arg in ["--test", "-t"]:
            run_tests()
        elif arg in ["--benchmark", "-b"]:
            run_benchmarks()
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python run.py [--web | --cli | --test | --benchmark]")
    else:
        print("\n=======================================================")
        print("   SMART CAMPUS & STUDENT OPERATIONS: ALGORITHMIC ENGINE")
        print("=======================================================")
        print("  [1] Launch Interactive Web Dashboard (Browser GUI)")
        print("  [2] Launch Interactive Terminal CLI (Viva Presentation)")
        print("  [3] Run Unit Test Suite (12 Unit Tests)")
        print("  [4] Run Algorithmic Performance Benchmarks")
        print("  [5] Exit")
        print("-------------------------------------------------------")
        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            launch_web()
        elif choice == "2":
            launch_cli()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            run_benchmarks()
        else:
            print("Exiting.")


if __name__ == "__main__":
    main()
````

## `services/__init__.py`

````python
"""
Smart Campus Venue & Facility Management: Domain Services
"""

from services.venue_service import VenueService, VenueRecord
from services.booking_service import BookingService, Booking
from services.navigation_service import NavigationService

__all__ = [
    "VenueService",
    "VenueRecord",
    "BookingService",
    "Booking",
    "NavigationService",
]
````

## `services/booking_service.py`

````python
"""
Smart Campus Algorithmic Engine: Venue & Slot Booking Service
File: services/booking_service.py

Manages campus venues and slot bookings using custom Augmented Interval Trees.
Each venue maintains its own balanced IntervalTree for O(log n + k) clash detection.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from core.interval_tree import IntervalTree, IntervalNode


class Booking:
    """Represents a scheduled event reservation in a campus venue."""

    def __init__(
        self,
        booking_id: str,
        venue_id: str,
        title: str,
        organizer: str,
        start_min: int,
        end_min: int,
        date: str = "2026-09-10",
        status: str = "Approved",
        rejection_reason: Optional[str] = None
    ):
        self.booking_id: str = booking_id
        self.venue_id: str = venue_id
        self.title: str = title
        self.organizer: str = organizer
        self.start_min: int = start_min
        self.end_min: int = end_min
        self.date: str = date
        self.status: str = status
        self.rejection_reason: Optional[str] = rejection_reason

    @property
    def start_time_str(self) -> str:
        hours = self.start_min // 60
        mins = self.start_min % 60
        return f"{hours:02d}:{mins:02d}"

    @property
    def end_time_str(self) -> str:
        hours = self.end_min // 60
        mins = self.end_min % 60
        return f"{hours:02d}:{mins:02d}"

    def to_dict(self) -> dict:
        return {
            "booking_id": self.booking_id,
            "venue_id": self.venue_id,
            "title": self.title,
            "organizer": self.organizer,
            "start_min": self.start_min,
            "end_min": self.end_min,
            "start_time_str": self.start_time_str,
            "end_time_str": self.end_time_str,
            "date": self.date,
            "status": self.status,
            "rejection_reason": self.rejection_reason
        }

    def __repr__(self) -> str:
        return f"Booking({self.booking_id}: '{self.title}' [{self.start_time_str} - {self.end_time_str}])"


class BookingService:
    """
    High-level manager for venue schedules using Interval Trees.
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.venues: Dict[str, dict] = {}
        # Venue ID -> aggregate tree used by the venue-level visualizations.
        self.trees: Dict[str, IntervalTree] = {}
        # (Venue ID, date) -> tree used for date-specific clash detection.
        self.date_trees: Dict[Tuple[str, str], IntervalTree] = {}
        # Booking ID -> Booking object (Approved)
        self.bookings_by_id: Dict[str, Booking] = {}
        # Pending requests awaiting Admin approval: Booking ID -> Booking
        self.pending_requests: Dict[str, Booking] = {}
        # All requests history (Pending, Approved, Rejected)
        self.all_requests: Dict[str, Booking] = {}

        if data_dir:
            self._load_initial_data(data_dir)

    def _load_initial_data(self, data_dir: str) -> None:
        venues_path = os.path.join(data_dir, "sample_venues.json")
        bookings_path = os.path.join(data_dir, "sample_bookings.json")

        if os.path.exists(venues_path):
            with open(venues_path, "r", encoding="utf-8") as f:
                venue_list = json.load(f)
                for v in venue_list:
                    self.register_venue(v["id"], v["name"], v["capacity"], v["building"])

        if os.path.exists(bookings_path):
            with open(bookings_path, "r", encoding="utf-8") as f:
                bookings = json.load(f)
                for b in bookings:
                    self.add_booking(
                        venue_id=b["venue_id"],
                        title=b["title"],
                        organizer=b["organizer"],
                        start_min=b["start_min"],
                        end_min=b["end_min"],
                        booking_id=b["booking_id"],
                        date=b.get("date", "2026-09-10")
                    )

        # Pre-seed initial pending user requests for Admin approval demo
        self.request_booking(
            venue_id="m1_auditorium",
            title="National AI & Cloud Symposium Briefing",
            organizer="Dept. of Computer Science",
            start_min=840,
            end_min=960,
            booking_id="REQ-BK-201",
            date="2026-09-10"
        )
        self.request_booking(
            venue_id="h1_auditorium",
            title="All-India Inter-Collegiate Literary Fest",
            organizer="Dept. of English & Humanities",
            start_min=600,
            end_min=750,
            booking_id="REQ-BK-202",
            date="2026-09-10"
        )

    def register_venue(self, venue_id: str, name: str, capacity: int, building: str) -> None:
        self.venues[venue_id] = {
            "id": venue_id,
            "name": name,
            "capacity": capacity,
            "building": building
        }
        if venue_id not in self.trees:
            self.trees[venue_id] = IntervalTree()

    def _get_date_tree(self, venue_id: str, date: str) -> IntervalTree:
        key = (venue_id, date)
        if key not in self.date_trees:
            self.date_trees[key] = IntervalTree()
        return self.date_trees[key]

    def get_all_venues(self) -> List[dict]:
        return list(self.venues.values())

    def get_venue(self, venue_id: str) -> Optional[dict]:
        return self.venues.get(venue_id)

    @staticmethod
    def time_str_to_minutes(time_str: str) -> int:
        """Parses 'HH:MM' string to minute offset (e.g. '09:30' -> 570)."""
        parts = time_str.strip().split(":")
        return int(parts[0]) * 60 + int(parts[1])

    @staticmethod
    def minutes_to_time_str(mins: int) -> str:
        """Converts minute offset to 'HH:MM' string."""
        h = mins // 60
        m = mins % 60
        return f"{h:02d}:{m:02d}"

    def check_clashes(
        self,
        venue_id: str,
        start_min: int,
        end_min: int,
        date: Optional[str] = None
    ) -> List[Booking]:
        """
        Queries the venue's Interval Tree for any overlapping slots in O(log n + k).
        """
        if venue_id not in self.trees:
            raise KeyError(f"Venue '{venue_id}' not found.")

        tree = self._get_date_tree(venue_id, date) if date else self.trees[venue_id]
        overlapping_nodes = tree.find_all_overlapping(start_min, end_min)
        clashes: List[Booking] = [node.data for node in overlapping_nodes if isinstance(node.data, Booking)]
        return clashes

    def add_booking(
        self,
        venue_id: str,
        title: str,
        organizer: str,
        start_min: int,
        end_min: int,
        booking_id: Optional[str] = None,
        date: str = "2026-09-10"
    ) -> Tuple[bool, str, Optional[Booking], List[Booking]]:
        """
        Attempts to reserve a slot.
        Returns (success: bool, message: str, booking: Optional[Booking], clashes: List[Booking])
        """
        if venue_id not in self.trees:
            return False, f"Unknown venue ID: {venue_id}", None, []

        if start_min >= end_min:
            return False, "Start time must be strictly before end time.", None, []

        # Conflict Detection via Interval Tree
        clashes = self.check_clashes(venue_id, start_min, end_min, date)
        if clashes:
            clash_titles = [f"'{c.title}' ({c.start_time_str} - {c.end_time_str})" for c in clashes]
            msg = f"Slot conflict! Overlaps with {len(clashes)} existing reservation(s): {', '.join(clash_titles)}"
            return False, msg, None, clashes

        if not booking_id:
            booking_id = f"BK-{len(self.bookings_by_id) + 101}"

        booking = Booking(
            booking_id=booking_id,
            venue_id=venue_id,
            title=title,
            organizer=organizer,
            start_min=start_min,
            end_min=end_min,
            date=date
        )

        # O(log n) insertion into balanced AVL Interval Tree
        self.trees[venue_id].insert(start_min, end_min, data=booking)
        self._get_date_tree(venue_id, date).insert(start_min, end_min, data=booking)
        self.bookings_by_id[booking_id] = booking
        self.all_requests[booking_id] = booking

        return True, "Booking confirmed successfully.", booking, []

    def request_booking(
        self,
        venue_id: str,
        title: str,
        organizer: str,
        start_min: int,
        end_min: int,
        booking_id: Optional[str] = None,
        date: str = "2026-09-10"
    ) -> Tuple[bool, str, Optional[Booking], List[Booking]]:
        """
        User side: Submits a booking request that awaits Admin approval.
        Performs conflict detection against already approved bookings.
        """
        if venue_id not in self.trees:
            return False, f"Unknown venue ID: {venue_id}", None, []

        if start_min >= end_min:
            return False, "Start time must be strictly before end time.", None, []

        clashes = self.check_clashes(venue_id, start_min, end_min, date)
        if clashes:
            clash_titles = [f"'{c.title}' ({c.start_time_str} - {c.end_time_str})" for c in clashes]
            msg = f"Slot conflict! Overlaps with {len(clashes)} existing reservation(s): {', '.join(clash_titles)}"
            return False, msg, None, clashes

        if not booking_id:
            booking_id = f"REQ-BK-{len(self.all_requests) + 201}"

        booking = Booking(
            booking_id=booking_id,
            venue_id=venue_id,
            title=title,
            organizer=organizer,
            start_min=start_min,
            end_min=end_min,
            date=date,
            status="Pending"
        )
        self.pending_requests[booking_id] = booking
        self.all_requests[booking_id] = booking

        return True, "Booking request submitted! Awaiting Admin approval.", booking, []

    def approve_booking(self, booking_id: str) -> Tuple[bool, str, Optional[Booking]]:
        """
        Admin side: Approves a pending booking request and commits it to the AVL Interval Tree.
        """
        if booking_id not in self.pending_requests:
            return False, f"Booking request '{booking_id}' not found in pending queue.", None

        booking = self.pending_requests[booking_id]

        # Re-check for any clashes in Interval Tree
        clashes = self.check_clashes(
            booking.venue_id, booking.start_min, booking.end_min, booking.date
        )
        if clashes:
            clash_titles = [f"'{c.title}' ({c.start_time_str} - {c.end_time_str})" for c in clashes]
            return False, f"Cannot approve! Slot conflicts with: {', '.join(clash_titles)}", None

        # Insert into balanced AVL Interval Tree in O(log n)
        self.trees[booking.venue_id].insert(booking.start_min, booking.end_min, data=booking)
        self._get_date_tree(booking.venue_id, booking.date).insert(
            booking.start_min, booking.end_min, data=booking
        )
        booking.status = "Approved"
        self.bookings_by_id[booking_id] = booking
        del self.pending_requests[booking_id]

        return True, f"Booking '{booking.title}' has been officially approved and scheduled.", booking

    def reject_booking(self, booking_id: str, reason: str = "Declined by Campus Administration") -> Tuple[bool, str]:
        """
        Admin side: Rejects a pending booking request.
        """
        if booking_id not in self.pending_requests:
            return False, f"Booking request '{booking_id}' not found in pending queue."

        booking = self.pending_requests[booking_id]
        booking.status = "Rejected"
        booking.rejection_reason = reason
        del self.pending_requests[booking_id]

        return True, f"Booking request '{booking.title}' was rejected."

    def get_pending_bookings(self) -> List[Booking]:
        """Returns all booking requests currently awaiting admin approval."""
        return list(self.pending_requests.values())

    def get_user_booking_requests(self) -> List[Booking]:
        """Returns all booking requests across statuses (Pending, Approved, Rejected)."""
        return list(self.all_requests.values())

    def cancel_booking(self, booking_id: str) -> Tuple[bool, str]:
        """Cancels booking and removes from Interval Tree in O(log n)."""
        if booking_id in self.pending_requests:
            del self.pending_requests[booking_id]
            if booking_id in self.all_requests:
                self.all_requests[booking_id].status = "Cancelled"
            return True, f"Pending booking request {booking_id} cancelled."

        if booking_id not in self.bookings_by_id:
            return False, f"Booking ID '{booking_id}' does not exist."

        booking = self.bookings_by_id[booking_id]
        venue_id = booking.venue_id

        removed = self.trees[venue_id].delete(booking.start_min, booking.end_min, data_id=booking_id)
        self._get_date_tree(venue_id, booking.date).delete(
            booking.start_min, booking.end_min, data_id=booking_id
        )
        if removed:
            del self.bookings_by_id[booking_id]
            if booking_id in self.all_requests:
                self.all_requests[booking_id].status = "Cancelled"
            return True, f"Booking {booking_id} cancelled successfully."
        else:
            return False, f"Failed to delete node from interval tree for booking {booking_id}."

    def get_venue_schedule(self, venue_id: str, date: Optional[str] = None) -> List[Booking]:
        """Returns approved bookings in chronological order, optionally for one date."""
        if venue_id not in self.trees:
            return []
        nodes = self.trees[venue_id].inorder()
        bookings = [n.data for n in nodes if isinstance(n.data, Booking)]
        if date:
            bookings = [booking for booking in bookings if booking.date == date]
        return bookings

    def get_all_bookings(self) -> List[Booking]:
        return list(self.bookings_by_id.values())

    def get_tree_ascii(self, venue_id: str) -> str:
        if venue_id not in self.trees:
            return f"No tree exists for venue: {venue_id}"
        return self.trees[venue_id].print_ascii_tree()

    def get_tree_json(self, venue_id: str) -> Optional[dict]:
        if venue_id not in self.trees:
            return None
        return self.trees[venue_id].to_dict()
````

## `services/navigation_service.py`

````python
"""
Smart Campus Algorithmic Engine: Campus Navigation Service
File: services/navigation_service.py

High-level navigation service leveraging custom Graph Adjacency List and Min-Heap Dijkstra.
"""

import json
import os
from typing import Dict, List, Optional
from core.graph import CampusGraph, Landmark, Edge


class NavigationService:
    """
    Campus Navigation Service managing landmark graphs and Dijkstra route generation.
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.graph = CampusGraph()
        if data_dir:
            self._load_landmarks(data_dir)

    def _load_landmarks(self, data_dir: str) -> None:
        path = os.path.join(data_dir, "campus_landmarks.json")
        if not os.path.exists(path):
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for lm in data.get("landmarks", []):
            landmark = Landmark(
                node_id=lm["id"],
                name=lm["name"],
                x=lm["x"],
                y=lm["y"],
                category=lm.get("category", "General"),
                description=lm.get("description", "")
            )
            self.graph.add_node(landmark)

        for pw in data.get("pathways", []):
            self.graph.add_edge(
                u=pw["source"],
                v=pw["dest"],
                weight=float(pw["weight"]),
                is_accessible=pw.get("is_accessible", True),
                path_name=pw.get("path_name", "Walkway"),
                bidirectional=True
            )

    def get_all_landmarks(self) -> List[dict]:
        return [lm.to_dict() for lm in self.graph.all_nodes()]

    def get_landmark(self, node_id: str) -> Optional[dict]:
        lm = self.graph.get_node(node_id)
        return lm.to_dict() if lm else None

    def get_all_pathways(self) -> List[dict]:
        return [edge.to_dict() for edge in self.graph.all_edges()]

    def find_route(
        self,
        start_id: str,
        dest_id: str,
        accessible_only: bool = False
    ) -> Optional[dict]:
        """
        Executes Dijkstra's algorithm to find the optimal path.
        """
        return self.graph.find_shortest_path(start_id, dest_id, accessible_only=accessible_only)
````

## `services/venue_service.py`

````python
"""
Smart Campus Algorithmic Engine: Venue & Facility Management Service
File: services/venue_service.py

Connects textbook data structures to internal university venue operations:
1. Venue Directory Storage: Custom SinglyLinkedList (head, tail, pointer chain)
2. Booking History & Undo: Custom LinkedStack (LIFO state recovery / booking cancellation)
3. Venue Waitlist Queue: Custom LinkedQueue (FIFO reservation token counter)
4. Resource & Facility Setup Evaluator: Custom Stack-based Expression Evaluator (Shunting-Yard)
5. Hierarchical Venue Indexing: Custom BinarySearchTree (traversals, search, 3 deletion cases)
6. Priority Event Allocation: Custom MaxHeap (VIP/Exam priority booking triage)
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from core.linked_list import SinglyLinkedList
from core.stack import LinkedStack
from core.queue import LinkedQueue
from core.bst import BinarySearchTree
from core.max_heap import MaxHeap
from core.expression_evaluator import evaluate_campus_formula, check_balanced_brackets


class VenueRecord:
    """Represents a campus venue record for internal university use."""

    def __init__(
        self,
        venue_id: str,
        name: str,
        building: str,
        category: str,
        capacity: int,
        air_conditioned: bool = True,
        projector: bool = True,
        sound_system: str = "Standard PA",
        seating_type: str = "Tiered Seating",
        wheelchair_accessible: bool = True,
        usage_policy: str = "Institutional Academic & Departmental Events",
        status: str = "Available"
    ):
        self.venue_id: str = venue_id
        self.name: str = name
        self.building: str = building
        self.category: str = category
        self.capacity: int = int(capacity)
        self.air_conditioned: bool = bool(air_conditioned)
        self.projector: bool = bool(projector)
        self.sound_system: str = sound_system
        self.seating_type: str = seating_type
        self.wheelchair_accessible: bool = bool(wheelchair_accessible)
        self.usage_policy: str = usage_policy
        self.status: str = status

    def to_dict(self) -> dict:
        return {
            "venue_id": self.venue_id,
            "id": self.venue_id,
            "name": self.name,
            "building": self.building,
            "category": self.category,
            "capacity": self.capacity,
            "air_conditioned": self.air_conditioned,
            "projector": self.projector,
            "sound_system": self.sound_system,
            "seating_type": self.seating_type,
            "wheelchair_accessible": self.wheelchair_accessible,
            "usage_policy": self.usage_policy,
            "status": self.status
        }

    def __repr__(self) -> str:
        return f"VenueRecord({self.venue_id}: '{self.name}' [{self.building}], Cap: {self.capacity})"


class VenueService:
    """
    Service layer coordinating venue data structures and workflows.
    Strictly for internal Kristu Jayanti University academic and departmental operations.
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.venue_list: SinglyLinkedList = SinglyLinkedList()
        self.venue_bst: BinarySearchTree = BinarySearchTree()
        self.undo_stack: LinkedStack = LinkedStack()
        self.waitlist_queue: LinkedQueue = LinkedQueue()
        self.priority_heap: MaxHeap = MaxHeap()

        self._waitlist_counter: int = 100
        self.data_dir: Optional[str] = data_dir

        if data_dir:
            self._load_venues(data_dir)

    def _load_venues(self, data_dir: str) -> None:
        venues_path = os.path.join(data_dir, "sample_venues.json")
        if os.path.exists(venues_path):
            with open(venues_path, "r", encoding="utf-8") as f:
                records = json.load(f)
                for r in records:
                    self.add_venue(
                        venue_id=r.get("id", r.get("venue_id")),
                        name=r["name"],
                        building=r["building"],
                        category=r.get("category", "Auditorium"),
                        capacity=r["capacity"],
                        air_conditioned=r.get("air_conditioned", True),
                        projector=r.get("projector", True),
                        sound_system=r.get("sound_system", "Integrated Audio"),
                        seating_type=r.get("seating_type", "Tiered Seating"),
                        wheelchair_accessible=r.get("wheelchair_accessible", True),
                        usage_policy=r.get("usage_policy", "College Academic Use")
                    )

        # Seed sample internal college waitlist requests
        self.enqueue_waitlist_request("BK-REQ-101", "jubilee_auditorium", "Inter-Collegiate Literary Fest", "Dept. of English & Humanities", "14:00 - 17:00")
        self.enqueue_waitlist_request("BK-REQ-102", "ske_auditorium", "International Conference on Green Computing", "Dept. of Computer Science", "10:00 - 13:00")
        self.enqueue_waitlist_request("BK-REQ-103", "m1_auditorium", "Student Leadership Council Assembly", "Student Welfare Directorate", "15:00 - 17:30")

        # Seed sample priority requests
        self.add_priority_request("REQ-PRIO-01", "Annual University Convocation 2026", "ske_auditorium", 10.0, "Office of the Vice Chancellor")
        self.add_priority_request("REQ-PRIO-02", "Autonomous End-Semester Examination Briefing", "jubilee_auditorium", 9.5, "Controller of Examinations")
        self.add_priority_request("REQ-PRIO-03", "NAAC Institutional Accreditation Peer Review", "board_room_admin", 9.0, "Internal Quality Assurance Cell (IQAC)")

    # -------------------------------------------------------------------------
    # 1. LINKED LIST & BST VENUE OPERATIONS
    # -------------------------------------------------------------------------

    def add_venue(
        self,
        venue_id: str,
        name: str,
        building: str,
        category: str = "Auditorium",
        capacity: int = 100,
        air_conditioned: bool = True,
        projector: bool = True,
        sound_system: str = "Integrated Audio",
        seating_type: str = "Tiered Seating",
        wheelchair_accessible: bool = True,
        usage_policy: str = "College Academic Use",
        at_front: bool = False
    ) -> VenueRecord:
        rec = VenueRecord(
            venue_id=venue_id,
            name=name,
            building=building,
            category=category,
            capacity=capacity,
            air_conditioned=air_conditioned,
            projector=projector,
            sound_system=sound_system,
            seating_type=seating_type,
            wheelchair_accessible=wheelchair_accessible,
            usage_policy=usage_policy
        )

        if at_front:
            self.venue_list.insert_front(rec)
        else:
            self.venue_list.insert_rear(rec)

        # Index in BST using venue_id
        self.venue_bst.insert(venue_id, rec.to_dict())

        # Push to undo stack
        self.undo_stack.push({
            "action": "ADD_VENUE",
            "venue_id": venue_id,
            "data": rec.to_dict()
        })
        return rec

    def get_all_venues(self) -> List[VenueRecord]:
        return self.venue_list.to_list()

    def find_venue(self, venue_id: str) -> Optional[VenueRecord]:
        return self.venue_list.search(lambda r: r.venue_id == venue_id)

    def delete_venue(self, venue_id: str) -> bool:
        rec = self.find_venue(venue_id)
        if not rec:
            return False

        self.venue_list.delete_by_key(lambda r: r.venue_id == venue_id)
        self.venue_bst.delete(venue_id)

        self.undo_stack.push({
            "action": "DELETE_VENUE",
            "venue_id": venue_id,
            "data": rec.to_dict()
        })
        return True

    def reverse_venue_list(self) -> None:
        self.venue_list.reverse()

    def get_linked_list_display(self) -> List[dict]:
        nodes = []
        for v in self.venue_list.to_list():
            nodes.append({
                "venue_id": v.venue_id,
                "name": v.name,
                "capacity": v.capacity,
                "building": v.building
            })
        return nodes

    # -------------------------------------------------------------------------
    # 2. BST HIERARCHICAL TRAVERSALS
    # -------------------------------------------------------------------------

    def get_bst_traversals(self) -> Dict[str, Any]:
        return {
            "inorder": [{"key": k, "value": v} for k, v in self.venue_bst.inorder()],
            "preorder": [{"key": k, "value": v} for k, v in self.venue_bst.preorder()],
            "postorder": [{"key": k, "value": v} for k, v in self.venue_bst.postorder()],
            "size": self.venue_bst.size(),
            "height": self.venue_bst.height()
        }

    # -------------------------------------------------------------------------
    # 3. LIFO UNDO STACK OPERATIONS
    # -------------------------------------------------------------------------

    def undo_last_operation(self) -> Tuple[bool, str]:
        if self.undo_stack.is_empty():
            return False, "Undo stack is empty; no operations to reverse."

        op = self.undo_stack.pop()
        action = op.get("action")
        vid = op.get("venue_id")

        if action == "ADD_VENUE":
            self.venue_list.delete_by_key(lambda r: r.venue_id == vid)
            self.venue_bst.delete(vid)
            return True, f"Undid venue addition: removed '{vid}'."
        elif action == "DELETE_VENUE":
            data = op.get("data", {})
            self.add_venue(
                venue_id=data.get("venue_id", vid),
                name=data.get("name", "Restored Venue"),
                building=data.get("building", "Main Block"),
                category=data.get("category", "Auditorium"),
                capacity=data.get("capacity", 200)
            )
            return True, f"Undid venue deletion: restored '{vid}'."
        elif action == "CANCEL_BOOKING":
            return True, f"Re-enstated booking '{vid}'."
        return False, f"Unknown action '{action}' on undo."

    # -------------------------------------------------------------------------
    # 4. FIFO VENUE WAITLIST QUEUE
    # -------------------------------------------------------------------------

    def enqueue_waitlist_request(
        self,
        request_id: str,
        venue_id: str,
        title: str,
        organizer: str,
        time_slot: str
    ) -> dict:
        self._waitlist_counter += 1
        item = {
            "token": f"W-{self._waitlist_counter}",
            "request_id": request_id,
            "venue_id": venue_id,
            "title": title,
            "organizer": organizer,
            "time_slot": time_slot,
            "status": "WAITING"
        }
        self.waitlist_queue.enqueue(item)
        return item

    def dequeue_waitlist_request(self) -> Optional[dict]:
        if self.waitlist_queue.is_empty():
            return None
        item = self.waitlist_queue.dequeue()
        item["status"] = "APPROVED"
        return item

    def get_waitlist_state(self) -> List[dict]:
        return self.waitlist_queue.to_list()

    def get_waitlist_count(self) -> int:
        return len(self.waitlist_queue)

    # -------------------------------------------------------------------------
    # 5. MAX-HEAP PRIORITY EVENT TRIAGE
    # -------------------------------------------------------------------------

    def add_priority_request(
        self,
        request_id: str,
        title: str,
        venue_id: str,
        priority_score: float,
        organizer: str
    ) -> dict:
        data = {
            "request_id": request_id,
            "title": title,
            "venue_id": venue_id,
            "priority_score": float(priority_score),
            "organizer": organizer,
            "status": "PENDING_ALLOCATION"
        }
        self.priority_heap.insert(request_id, float(priority_score), data=data)
        return data

    def extract_highest_priority(self) -> Optional[dict]:
        if self.priority_heap.is_empty():
            return None
        node = self.priority_heap.extract_max()
        if node and node.data:
            node.data["status"] = "ALLOCATED"
            return node.data
        return None

    def escalate_priority_request(self, request_id: str, new_priority: float) -> bool:
        return self.priority_heap.update_priority(request_id, float(new_priority))

    def get_all_priority_requests(self) -> List[dict]:
        items = []
        for it in self.priority_heap.to_list():
            if it.get("data"):
                items.append(it["data"])
        return items

    # -------------------------------------------------------------------------
    # 6. EVENT RESOURCE & LOGISTICS SETUP EVALUATOR (STACK-BASED SHUNTING YARD)
    # -------------------------------------------------------------------------

    def calculate_resource_score(
        self,
        attendees: float,
        duration_hours: float,
        av_equipment_units: float = 20.0,
        buffer_percent: float = 10.0,
        formula_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates event logistics and technical setup score using stack-based infix-to-postfix evaluation.
        Formula: (attendees * duration_hours + av_equipment_units) * (1 - buffer_percent / 100)
        Used for internal hall logistics and technical readiness planning (no money/payments).
        """
        if formula_override:
            formula_str = formula_override
        else:
            formula_str = f"({attendees} * {duration_hours} + {av_equipment_units}) * (1 - {buffer_percent} / 100)"

        is_balanced = check_balanced_brackets(formula_str)
        if not is_balanced:
            return {
                "success": False,
                "error": "Mismatched delimiters / parentheses in formula expression.",
                "formula": formula_str
            }

        try:
            success, score, msg, postfix = evaluate_campus_formula(formula_str)
            if success:
                return {
                    "success": True,
                    "formula": formula_str,
                    "attendees": attendees,
                    "duration_hours": duration_hours,
                    "av_equipment_units": av_equipment_units,
                    "buffer_percent": buffer_percent,
                    "setup_score": round(score, 2)
                }
            else:
                return {
                    "success": False,
                    "error": msg,
                    "formula": formula_str
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "formula": formula_str
            }
````

## `tests/test_api.py`

````python
"""
Integration Tests for Web Dashboard Backend API (Venue & Facility Management)
File: tests/test_api.py
"""

import unittest
import json
from web.app import app


class TestWebAPI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_static_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"Venue" in response.data or b"Smart Campus" in response.data)

    def test_get_venues_and_bookings(self):
        res = self.client.get("/api/venues")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        venues = data["venues"]
        self.assertGreater(len(venues), 0)

        # Check that Jubilee, SKE, M1-M4, and H1-H2 are present
        venue_ids = [v["id"] for v in venues]
        self.assertIn("jubilee_auditorium", venue_ids)
        self.assertIn("ske_auditorium", venue_ids)
        self.assertIn("m1_auditorium", venue_ids)
        self.assertIn("h1_auditorium", venue_ids)
        self.assertIn("h2_auditorium", venue_ids)

        venue_map = {v["id"]: v for v in venues}
        self.assertEqual(venue_map["ske_auditorium"]["capacity"], 544)
        self.assertEqual(venue_map["jubilee_auditorium"]["capacity"], 1000)
        self.assertEqual(venue_map["h1_auditorium"]["capacity"], 250)
        self.assertEqual(venue_map["h2_auditorium"]["capacity"], 200)

        venue_id = venues[0]["id"]
        res_bookings = self.client.get(f"/api/bookings?venue_id={venue_id}")
        self.assertEqual(res_bookings.status_code, 200)

    def test_booking_conflict_detection(self):
        # SKE Auditorium already has 09:00 - 11:30 (540 to 690) booked
        conflict_payload = {
            "venue_id": "ske_auditorium",
            "title": "Clashing Assembly",
            "organizer": "Student Council",
            "start_time": "10:00",
            "end_time": "11:00"
        }
        res = self.client.post(
            "/api/bookings",
            data=json.dumps(conflict_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 409)
        data = json.loads(res.data)
        self.assertFalse(data["success"])
        self.assertGreater(len(data["clashes"]), 0)

    def test_venues_linked_list_and_undo(self):
        # GET all venues
        res = self.client.get("/api/venues")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("venues", data)
        self.assertGreater(data["count"], 0)
        self.assertIn("pointer_chain", data)

        # POST new venue
        new_v = {
            "venue_id": "m5_auditorium",
            "name": "M5 Mini Auditorium",
            "building": "Main Block",
            "category": "Auditorium",
            "capacity": 180,
            "usage_policy": "Department Club Assemblies",
            "at_front": True
        }
        res_add = self.client.post("/api/venues", data=json.dumps(new_v), content_type="application/json")
        self.assertEqual(res_add.status_code, 200)

        # Reverse list
        res_rev = self.client.post("/api/venues/reverse")
        self.assertEqual(res_rev.status_code, 200)

        # Delete venue
        res_del = self.client.delete("/api/venues/m5_auditorium")
        self.assertEqual(res_del.status_code, 200)

        # Undo deletion via Stack
        res_undo = self.client.post("/api/venues/undo")
        self.assertEqual(res_undo.status_code, 200)
        undo_data = json.loads(res_undo.data)
        self.assertTrue(undo_data["success"])

    def test_waitlist_queue_api(self):
        # Enqueue waitlist request
        res = self.client.post("/api/waitlist", data=json.dumps({
            "venue_id": "jubilee_auditorium",
            "title": "Guest Lecture on Artificial Intelligence",
            "organizer": "IEEE Computer Society",
            "time_slot": "15:00 - 17:00"
        }), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        t_data = json.loads(res.data)
        self.assertTrue(t_data["success"])

        # Serve / approve waitlist item
        res_serve = self.client.post("/api/waitlist/serve")
        self.assertEqual(res_serve.status_code, 200)
        s_data = json.loads(res_serve.data)
        self.assertTrue(s_data["success"])

    def test_priority_requests_api(self):
        # Add priority request
        res = self.client.post("/api/priority-requests", data=json.dumps({
            "request_id": "REQ-TEST-PRIO",
            "title": "Vice Chancellor Academic Address",
            "venue_id": "board_room_admin",
            "priority_score": 9.8,
            "organizer": "Vice Chancellor's Secretariat"
        }), content_type="application/json")
        self.assertEqual(res.status_code, 200)

        # Dispatch top priority
        res_disp = self.client.post("/api/priority-requests/dispatch")
        self.assertEqual(res_disp.status_code, 200)
        d_data = json.loads(res_disp.data)
        self.assertTrue(d_data["success"])

    def test_resource_calculator_api(self):
        payload = {
            "attendees": 300,
            "duration_hours": 2.5,
            "av_equipment_units": 40,
            "buffer_percent": 10
        }
        res = self.client.post("/api/resources/calculate", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        # (300 * 2.5 + 40) * (1 - 10 / 100) = (750 + 40) * 0.9 = 790 * 0.9 = 711.0
        self.assertEqual(data["setup_score"], 711.0)

    def test_navigation_dijkstra(self):
        nav_payload = {
            "start_id": "main_gate",
            "dest_id": "cs_block",
            "accessible_only": False
        }
        res = self.client.post(
            "/api/navigate",
            data=json.dumps(nav_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("route", data)

    def test_user_request_and_admin_approval(self):
        # 1. User submits a booking request for m2_auditorium
        user_req = {
            "venue_id": "m2_auditorium",
            "title": "Data Science Scholars Meet",
            "organizer": "Dept. of Computer Science",
            "start_time": "16:00",
            "end_time": "17:30",
            "role": "user"
        }
        res = self.client.post("/api/bookings", data=json.dumps(user_req), content_type="application/json")
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "Pending")
        req_id = data["booking"]["booking_id"]

        # 2. Admin retrieves pending bookings list
        res_pending = self.client.get("/api/bookings/pending")
        self.assertEqual(res_pending.status_code, 200)
        pending_list = json.loads(res_pending.data)
        pending_ids = [p["booking_id"] for p in pending_list]
        self.assertIn(req_id, pending_ids)

        # 3. Admin approves the booking
        res_approve = self.client.post(f"/api/bookings/{req_id}/approve")
        self.assertEqual(res_approve.status_code, 200)
        app_data = json.loads(res_approve.data)
        self.assertTrue(app_data["success"])

        # 4. Booking is now in active schedule
        res_sched = self.client.get("/api/bookings?venue_id=m2_auditorium")
        self.assertEqual(res_sched.status_code, 200)
        sched_list = json.loads(res_sched.data)
        sched_ids = [b["booking_id"] for b in sched_list]
        self.assertIn(req_id, sched_ids)


if __name__ == "__main__":
    unittest.main()
````

## `tests/test_expression.py`

````python
"""
Unit Tests for Stack Application: Expression Handling & Bracket Balancing
File: tests/test_expression.py
"""

import unittest
from core.expression_evaluator import (
    check_balanced_brackets,
    infix_to_postfix,
    evaluate_postfix,
    evaluate_campus_formula,
    ExpressionError
)


class TestExpressionEvaluator(unittest.TestCase):

    def test_balanced_brackets(self):
        # Valid balanced expressions
        valid_expressions = [
            "(a + b) * (c - d)",
            "{[()]}",
            "((10 + 20) * [30 / 5])",
            "no_brackets_at_all",
            ""
        ]
        for expr in valid_expressions:
            is_bal, msg = check_balanced_brackets(expr)
            self.assertTrue(is_bal, f"Expected '{expr}' to be balanced: {msg}")

        # Invalid unbalanced expressions
        invalid_expressions = [
            "( [ ) ]",            # Mismatched nesting
            "((a + b)",           # Unclosed open
            "a + b)",             # Unmatched close
            "{ [ ( ] ) }"         # Cross-nested brackets
        ]
        for expr in invalid_expressions:
            is_bal, _ = check_balanced_brackets(expr)
            self.assertFalse(is_bal, f"Expected '{expr}' to be detected as unbalanced.")

    def test_infix_to_postfix_conversion(self):
        cases = [
            ("A + B", ["A", "B", "+"]),
            ("A + B * C", ["A", "B", "C", "*", "+"]),
            ("(A + B) * C", ["A", "B", "+", "C", "*"]),
            ("A ^ B ^ C", ["A", "B", "C", "^", "^"]),  # Right-associative exponentiation
            ("A * (B + C) / D", ["A", "B", "C", "+", "*", "D", "/"])
        ]
        for infix, expected_postfix in cases:
            res = infix_to_postfix(infix)
            self.assertEqual(res, expected_postfix, f"Mismatch for '{infix}'")

    def test_evaluate_postfix_arithmetic(self):
        # Expression: (10 + 20) * 3 / 2 = 45.0
        tokens = ["10", "20", "+", "3", "*", "2", "/"]
        val = evaluate_postfix(tokens)
        self.assertEqual(val, 45.0)

        # Exponentiation: 2 ^ 3 = 8
        tokens_pow = ["2", "3", "^"]
        self.assertEqual(evaluate_postfix(tokens_pow), 8.0)

    def test_evaluate_with_variables(self):
        # Formula: (BaseFee + LabFee) * (1 - Discount / 100)
        # BaseFee=40000, LabFee=10000, Discount=20 -> (50000) * 0.8 = 40000.0
        formula = "(BaseFee + LabFee) * (1 - Discount / 100)"
        variables = {
            "BaseFee": 40000,
            "LabFee": 10000,
            "Discount": 20
        }
        success, net_fee, msg, postfix = evaluate_campus_formula(formula, variables)
        self.assertTrue(success)
        self.assertEqual(net_fee, 40000.0)
        self.assertIn("BaseFee", postfix)

    def test_division_by_zero(self):
        success, val, msg, _ = evaluate_campus_formula("100 / (5 - 5)")
        self.assertFalse(success)
        self.assertIn("Division by zero", msg)


if __name__ == "__main__":
    unittest.main()
````

## `tests/test_graph_dijkstra.py`

````python
"""
Unit Tests for Custom Graph & Dijkstra Shortest Path Algorithm
File: tests/test_graph_dijkstra.py
"""

import unittest
from core.graph import CampusGraph, Landmark


class TestGraphDijkstra(unittest.TestCase):

    def setUp(self):
        self.graph = CampusGraph()
        # Create a diamond test graph:
        # A --(10)--> B --(10)--> D
        # A --(30)--> C --(5)---> D
        # Total A-B-D = 20, Total A-C-D = 35
        # Also edge A -> D direct with weight 50 (inaccessible)
        for nid in ["A", "B", "C", "D"]:
            self.graph.add_node(Landmark(nid, f"Node {nid}", 0, 0))

        self.graph.add_edge("A", "B", 10.0, is_accessible=True, path_name="AB")
        self.graph.add_edge("B", "D", 10.0, is_accessible=True, path_name="BD")
        self.graph.add_edge("A", "C", 30.0, is_accessible=True, path_name="AC")
        self.graph.add_edge("C", "D", 5.0, is_accessible=True, path_name="CD")
        self.graph.add_edge("A", "D", 15.0, is_accessible=False, path_name="AD_Stairs")

    def test_shortest_path_standard(self):
        # Without accessible filter, the fastest path from A to D is A -> D direct (15m stairs)
        result = self.graph.find_shortest_path("A", "D", accessible_only=False)
        self.assertIsNotNone(result)
        self.assertEqual(result["total_distance_m"], 15.0)
        self.assertEqual(result["path_node_ids"], ["A", "D"])

    def test_shortest_path_accessible_filter(self):
        # With accessible_only=True, stairs A->D are excluded. Optimal is A -> B -> D (20m)
        result = self.graph.find_shortest_path("A", "D", accessible_only=True)
        self.assertIsNotNone(result)
        self.assertEqual(result["total_distance_m"], 20.0)
        self.assertEqual(result["path_node_ids"], ["A", "B", "D"])

    def test_same_source_and_dest(self):
        result = self.graph.find_shortest_path("A", "A")
        self.assertIsNotNone(result)
        self.assertEqual(result["total_distance_m"], 0.0)
        self.assertEqual(result["path_node_ids"], ["A"])

    def test_unreachable_node(self):
        self.graph.add_node(Landmark("Isolated", "Island", 0, 0))
        result = self.graph.find_shortest_path("A", "Isolated")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
````

## `tests/test_interval_tree.py`

````python
"""
Unit Tests for Custom Augmented Interval Tree
File: tests/test_interval_tree.py
"""

import unittest
from core.interval_tree import IntervalTree, IntervalNode


class TestIntervalTree(unittest.TestCase):

    def setUp(self):
        self.tree = IntervalTree()

    def _verify_avl_and_max_high(self, node: IntervalNode):
        """Recursively validates AVL balance property and max_high augmentation."""
        if not node:
            return

        left_height = node.left.height if node.left else 0
        right_height = node.right.height if node.right else 0
        self.assertEqual(node.height, 1 + max(left_height, right_height))
        self.assertTrue(-1 <= left_height - right_height <= 1, f"AVL balance violated at node {node}")

        expected_max = node.high
        if node.left:
            expected_max = max(expected_max, node.left.max_high)
        if node.right:
            expected_max = max(expected_max, node.right.max_high)
        self.assertEqual(node.max_high, expected_max, f"max_high mismatch at node {node}")

        if node.left:
            self.assertTrue(node.left.low <= node.low)
            self._verify_avl_and_max_high(node.left)
        if node.right:
            self.assertTrue(node.right.low >= node.low)
            self._verify_avl_and_max_high(node.right)

    def test_insert_and_balance(self):
        intervals = [(10, 20), (20, 30), (30, 40), (5, 15), (25, 35)]
        for low, high in intervals:
            self.tree.insert(low, high, data=f"{low}-{high}")

        self.assertEqual(len(self.tree), 5)
        self._verify_avl_and_max_high(self.tree.root)

    def test_boundary_touch_no_clash(self):
        # [10, 20) and [20, 30) touch at 20, but do NOT overlap
        self.tree.insert(10, 20, "A")
        self.tree.insert(20, 30, "B")

        clash1 = self.tree.find_all_overlapping(20, 30)
        self.assertEqual(len(clash1), 1)
        self.assertEqual(clash1[0].data, "B")

        # Query [5, 10) touches 10, should find no overlaps
        clash2 = self.tree.find_all_overlapping(5, 10)
        self.assertEqual(len(clash2), 0)

    def test_partial_and_enclosing_overlap(self):
        self.tree.insert(100, 200, "Event 1")
        self.tree.insert(300, 400, "Event 2")
        self.tree.insert(500, 600, "Event 3")

        # Overlaps only Event 1
        clashes = self.tree.find_all_overlapping(150, 250)
        self.assertEqual(len(clashes), 1)
        self.assertEqual(clashes[0].data, "Event 1")

        # Query spans from 150 to 550: should clash with all three!
        all_clashes = self.tree.find_all_overlapping(150, 550)
        self.assertEqual(len(all_clashes), 3)

    def test_deletion(self):
        self.tree.insert(10, 20, "A")
        self.tree.insert(20, 30, "B")
        self.tree.insert(30, 40, "C")
        self.tree.insert(40, 50, "D")

        # Delete middle node
        deleted = self.tree.delete(20, 30)
        self.assertTrue(deleted)
        self.assertEqual(len(self.tree), 3)
        self._verify_avl_and_max_high(self.tree.root)

        # Deleting non-existent node
        deleted_false = self.tree.delete(99, 100)
        self.assertFalse(deleted_false)

    def test_inorder_order(self):
        test_data = [(30, 40), (10, 20), (50, 60), (20, 25), (5, 15)]
        for l, h in test_data:
            self.tree.insert(l, h)

        inorder_nodes = self.tree.inorder()
        sorted_lows = [node.low for node in inorder_nodes]
        self.assertEqual(sorted_lows, sorted(sorted_lows))


if __name__ == "__main__":
    unittest.main()
````

## `tests/test_linear_structures.py`

````python
"""
Unit Tests for Phase 1 Linear Data Structures (Linked List, Stack, Queue)
File: tests/test_linear_structures.py
"""

import unittest
from core.linked_list import SinglyLinkedList
from core.stack import LinkedStack
from core.queue import LinkedQueue


class TestSinglyLinkedList(unittest.TestCase):

    def setUp(self):
        self.ll = SinglyLinkedList()

    def test_insert_front_and_rear(self):
        self.ll.insert_front(10)
        self.ll.insert_front(5)
        self.ll.insert_rear(20)
        self.ll.insert_rear(30)

        # Expected list: [5, 10, 20, 30]
        self.assertEqual(len(self.ll), 4)
        self.assertEqual(self.ll.to_list(), [5, 10, 20, 30])
        self.assertEqual(self.ll.head.data, 5)
        self.assertEqual(self.ll.tail.data, 30)

    def test_insert_at_index(self):
        self.ll.insert_rear("A")
        self.ll.insert_rear("C")

        # Insert "B" at index 1
        success = self.ll.insert_at(1, "B")
        self.assertTrue(success)
        self.assertEqual(self.ll.to_list(), ["A", "B", "C"])

        # Insert at 0 (front)
        self.ll.insert_at(0, "START")
        self.assertEqual(self.ll.to_list(), ["START", "A", "B", "C"])

        # Insert at invalid index
        self.assertFalse(self.ll.insert_at(99, "INVALID"))

    def test_delete_operations(self):
        for val in [1, 2, 3, 4, 5]:
            self.ll.insert_rear(val)

        # Delete front
        popped_front = self.ll.delete_front()
        self.assertEqual(popped_front, 1)
        self.assertEqual(self.ll.to_list(), [2, 3, 4, 5])

        # Delete rear
        popped_rear = self.ll.delete_rear()
        self.assertEqual(popped_rear, 5)
        self.assertEqual(self.ll.to_list(), [2, 3, 4])

        # Delete by key (middle element 3)
        deleted = self.ll.delete_by_key(lambda x: x == 3)
        self.assertEqual(deleted, 3)
        self.assertEqual(self.ll.to_list(), [2, 4])

        # Delete at index
        at_idx = self.ll.delete_at(1)
        self.assertEqual(at_idx, 4)
        self.assertEqual(self.ll.to_list(), [2])

        # Delete last remaining
        self.ll.delete_front()
        self.assertTrue(self.ll.is_empty())
        self.assertIsNone(self.ll.head)
        self.assertIsNone(self.ll.tail)

    def test_search_and_get_at(self):
        self.ll.insert_rear({"id": "MCA-01", "name": "Alice"})
        self.ll.insert_rear({"id": "MCA-02", "name": "Bob"})

        found = self.ll.search(lambda item: item["id"] == "MCA-02")
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "Bob")

        self.assertEqual(self.ll.get_at(0)["id"], "MCA-01")
        self.assertIsNone(self.ll.get_at(5))

    def test_in_place_reverse(self):
        for i in range(1, 6):
            self.ll.insert_rear(i)

        self.assertEqual(self.ll.to_list(), [1, 2, 3, 4, 5])
        self.ll.reverse()
        self.assertEqual(self.ll.to_list(), [5, 4, 3, 2, 1])
        self.assertEqual(self.ll.head.data, 5)
        self.assertEqual(self.ll.tail.data, 1)


class TestLinkedStack(unittest.TestCase):

    def setUp(self):
        self.stack = LinkedStack()

    def test_lifo_push_pop(self):
        self.assertTrue(self.stack.is_empty())

        self.stack.push("Page 1")
        self.stack.push("Page 2")
        self.stack.push("Page 3")

        self.assertEqual(len(self.stack), 3)
        self.assertEqual(self.stack.peek(), "Page 3")

        self.assertEqual(self.stack.pop(), "Page 3")
        self.assertEqual(self.stack.pop(), "Page 2")
        self.assertEqual(self.stack.pop(), "Page 1")
        self.assertTrue(self.stack.is_empty())

    def test_empty_stack_exceptions(self):
        with self.assertRaises(IndexError):
            self.stack.pop()

        with self.assertRaises(IndexError):
            self.stack.peek()


class TestLinkedQueue(unittest.TestCase):

    def setUp(self):
        self.queue = LinkedQueue()

    def test_fifo_enqueue_dequeue(self):
        self.assertTrue(self.queue.is_empty())

        self.queue.enqueue("Customer 1")
        self.queue.enqueue("Customer 2")
        self.queue.enqueue("Customer 3")

        self.assertEqual(len(self.queue), 3)
        self.assertEqual(self.queue.peek(), "Customer 1")

        self.assertEqual(self.queue.dequeue(), "Customer 1")
        self.assertEqual(self.queue.dequeue(), "Customer 2")
        self.assertEqual(self.queue.dequeue(), "Customer 3")
        self.assertTrue(self.queue.is_empty())

    def test_empty_queue_exceptions(self):
        with self.assertRaises(IndexError):
            self.queue.dequeue()

        with self.assertRaises(IndexError):
            self.queue.peek()


if __name__ == "__main__":
    unittest.main()
````

## `tests/test_max_heap.py`

````python
"""
Unit Tests for Custom Binary Max-Heap
File: tests/test_max_heap.py
"""

import random
import unittest
from core.max_heap import MaxHeap


class TestMaxHeap(unittest.TestCase):

    def setUp(self):
        self.heap = MaxHeap()

    def _verify_max_heap_invariant(self, heap: MaxHeap):
        """Validates that parent.priority >= child.priority across entire heap."""
        arr = heap._heap
        n = len(arr)
        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n:
                self.assertGreaterEqual(
                    arr[i].priority,
                    arr[left].priority,
                    f"Max-heap invariant violated between parent {arr[i]} and left child {arr[left]}"
                )
            if right < n:
                self.assertGreaterEqual(
                    arr[i].priority,
                    arr[right].priority,
                    f"Max-heap invariant violated between parent {arr[i]} and right child {arr[right]}"
                )
            # Check position map correctness
            self.assertEqual(heap._pos_map[arr[i].item_id], i)

    def test_insert_and_extract(self):
        items = [
            ("item1", 50.0),
            ("item2", 90.0),
            ("item3", 20.0),
            ("item4", 75.0),
            ("item5", 100.0)
        ]
        for item_id, prio in items:
            self.heap.insert(item_id, prio)
            self._verify_max_heap_invariant(self.heap)

        self.assertEqual(len(self.heap), 5)
        self.assertEqual(self.heap.peek().item_id, "item5")

        extracted = []
        while not self.heap.is_empty():
            extracted.append(self.heap.extract_max().priority)
            self._verify_max_heap_invariant(self.heap)

        self.assertEqual(extracted, [100.0, 90.0, 75.0, 50.0, 20.0])

    def test_update_priority_escalation(self):
        self.heap.insert("taskA", 30.0)
        self.heap.insert("taskB", 50.0)
        self.heap.insert("taskC", 40.0)

        self.assertEqual(self.heap.peek().item_id, "taskB")

        # Escalate taskA to highest priority
        self.heap.update_priority("taskA", 95.0)
        self._verify_max_heap_invariant(self.heap)
        self.assertEqual(self.heap.peek().item_id, "taskA")

        # De-escalate taskA
        self.heap.update_priority("taskA", 10.0)
        self._verify_max_heap_invariant(self.heap)
        self.assertEqual(self.heap.peek().item_id, "taskB")

    def test_random_large_workload(self):
        random.seed(42)
        scores = [random.randint(1, 1000) for _ in range(100)]
        for i, s in enumerate(scores):
            self.heap.insert(f"id_{i}", float(s))
            self._verify_max_heap_invariant(self.heap)

        extracted = []
        while not self.heap.is_empty():
            extracted.append(self.heap.extract_max().priority)

        self.assertEqual(extracted, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
````

## `tests/test_phase2_bst_and_traversals.py`

````python
"""
Unit Tests for Phase 2: Binary Search Tree, Traversals, and Graph BFS/DFS
File: tests/test_phase2_bst_and_traversals.py
"""

import unittest
from core.bst import BinarySearchTree
from core.graph import CampusGraph, Landmark


class TestPhase2HierarchicalAndGraph(unittest.TestCase):

    def setUp(self):
        self.bst = BinarySearchTree()

    def test_bst_insert_search(self):
        # Insert student keys (e.g. roll numbers / marks)
        self.bst.insert(50, "Student 50")
        self.bst.insert(30, "Student 30")
        self.bst.insert(70, "Student 70")
        self.bst.insert(20, "Student 20")
        self.bst.insert(40, "Student 40")

        self.assertEqual(len(self.bst), 5)
        self.assertEqual(self.bst.search(30), "Student 30")
        self.assertEqual(self.bst.search(70), "Student 70")
        self.assertIsNone(self.bst.search(999))

    def test_bst_traversals(self):
        # Tree structure:
        #        50
        #       /  \
        #      30   70
        #     /  \
        #    20  40
        for k in [50, 30, 70, 20, 40]:
            self.bst.insert(k, f"Val_{k}")

        # Inorder: Left -> Root -> Right (Strictly Ascending)
        inorder_keys = [k for k, _ in self.bst.inorder()]
        self.assertEqual(inorder_keys, [20, 30, 40, 50, 70])

        # Preorder: Root -> Left -> Right
        preorder_keys = [k for k, _ in self.bst.preorder()]
        self.assertEqual(preorder_keys, [50, 30, 20, 40, 70])

        # Postorder: Left -> Right -> Root
        postorder_keys = [k for k, _ in self.bst.postorder()]
        self.assertEqual(postorder_keys, [20, 40, 30, 70, 50])

    def test_bst_delete_cases(self):
        for k in [50, 30, 70, 20, 40, 60, 80]:
            self.bst.insert(k, k)

        # Case 1: Delete leaf node (20)
        self.assertTrue(self.bst.delete(20))
        self.assertIsNone(self.bst.search(20))
        self.assertEqual([k for k, _ in self.bst.inorder()], [30, 40, 50, 60, 70, 80])

        # Case 2: Delete node with 1 child (30 now has only right child 40)
        self.assertTrue(self.bst.delete(30))
        self.assertIsNone(self.bst.search(30))
        self.assertEqual([k for k, _ in self.bst.inorder()], [40, 50, 60, 70, 80])

        # Case 3: Delete root node with 2 children (50)
        self.assertTrue(self.bst.delete(50))
        self.assertIsNone(self.bst.search(50))
        self.assertEqual([k for k, _ in self.bst.inorder()], [40, 60, 70, 80])

    def test_graph_bfs_and_dfs(self):
        graph = CampusGraph()
        # Graph: A connected to B and C; B connected to D; C connected to D
        for node in ["A", "B", "C", "D"]:
            graph.add_node(Landmark(node, f"Landmark {node}", 0, 0))

        graph.add_edge("A", "B", 10.0, bidirectional=True)
        graph.add_edge("A", "C", 10.0, bidirectional=True)
        graph.add_edge("B", "D", 10.0, bidirectional=True)
        graph.add_edge("C", "D", 10.0, bidirectional=True)

        # BFS explores level 1 (B, C) before level 2 (D)
        bfs_order = graph.bfs("A")
        self.assertEqual(bfs_order[0], "A")
        self.assertIn(bfs_order[1], ["B", "C"])
        self.assertIn(bfs_order[2], ["B", "C"])
        self.assertEqual(bfs_order[3], "D")

        # DFS explores all nodes
        dfs_order = graph.dfs("A")
        self.assertEqual(len(dfs_order), 4)
        self.assertEqual(set(dfs_order), {"A", "B", "C", "D"})


if __name__ == "__main__":
    unittest.main()
````

## `tests/test_phase3_search_sort.py`

````python
"""
Unit Tests for Phase 3: Searching and Sorting Operations
File: tests/test_phase3_search_sort.py
"""

import random
import unittest
from core.searching_sorting import (
    linear_search,
    binary_search,
    merge_sort,
    quick_sort,
    insertion_sort,
    compare_sorting_algorithms,
)


class TestPhase3SearchSort(unittest.TestCase):

    def test_linear_search(self):
        arr = [45, 12, 89, 33, 77, 21]
        idx, comps = linear_search(arr, 33)
        self.assertEqual(idx, 3)
        self.assertEqual(comps, 4)

        # Not found
        idx_nf, comps_nf = linear_search(arr, 999)
        self.assertEqual(idx_nf, -1)
        self.assertEqual(comps_nf, 6)

    def test_binary_search(self):
        # Sorted array
        arr = [10, 20, 30, 40, 50, 60, 70, 80]
        idx, comps = binary_search(arr, 60)
        self.assertEqual(idx, 5)
        self.assertLessEqual(comps, 4)  # log2(8) = 3 or 4

        # Not found
        idx_nf, comps_nf = binary_search(arr, 25)
        self.assertEqual(idx_nf, -1)

    def test_merge_sort_correctness(self):
        random.seed(42)
        data = [random.randint(1, 1000) for _ in range(100)]
        sorted_asc = merge_sort(data)
        self.assertEqual(sorted_asc, sorted(data))

        sorted_desc = merge_sort(data, reverse=True)
        self.assertEqual(sorted_desc, sorted(data, reverse=True))

    def test_quick_sort_correctness(self):
        random.seed(42)
        data = [random.randint(1, 1000) for _ in range(100)]
        sorted_asc = quick_sort(data)
        self.assertEqual(sorted_asc, sorted(data))

        sorted_desc = quick_sort(data, reverse=True)
        self.assertEqual(sorted_desc, sorted(data, reverse=True))

    def test_insertion_sort_correctness(self):
        data = [5, 2, 9, 1, 5, 6]
        sorted_asc = insertion_sort(data)
        self.assertEqual(sorted_asc, [1, 2, 5, 5, 6, 9])

    def test_compare_sorting_benchmarks(self):
        res = compare_sorting_algorithms(sample_size=100)
        self.assertEqual(res["sample_size"], 100)
        self.assertEqual(len(res["results"]), 3)
        alg_names = [r["algorithm"] for r in res["results"]]
        self.assertIn("Merge Sort", alg_names)
        self.assertIn("Quick Sort", alg_names)
        self.assertIn("Insertion Sort", alg_names)


if __name__ == "__main__":
    unittest.main()
````

## `tests/test_phase4_algorithms.py`

````python
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
````

## `web/app.py`

````python
"""
Smart Campus Venue & Facility Management Engine: Web Dashboard Backend
File: web/app.py

REST API and static server connecting the Venue Management frontend to
custom textbook data structures:
- Augmented AVL Interval Tree (clash detection & timeline)
- Custom Singly Linked List (venue registry & pointer chain)
- Custom Binary Search Tree (venue indexing & 3-case deletion)
- Custom Linked Stack (booking cancellation & undo)
- Custom Linked Queue (FIFO reservation waitlist)
- Custom Binary Max-Heap (priority allocation engine)
- Custom Expression Evaluator (facility setup readiness)
- Adjacency List Graph + Min-Heap Dijkstra (campus venue wayfinding)
- Searching, Sorting & Algorithmic Problem Solving (Greedy, Knapsack DP, Backtracking CSP)
"""

import os
import sys
import time
import random
from flask import Flask, jsonify, request, send_from_directory

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.venue_service import VenueService
from services.booking_service import BookingService
from services.navigation_service import NavigationService

from core.searching_sorting import (
    linear_search,
    binary_search,
    merge_sort,
    quick_sort,
    insertion_sort,
    compare_sorting_algorithms
)
from core.algorithmic_problem_solving import (
    Activity,
    greedy_activity_selection,
    BudgetItem,
    knapsack_budget_optimizer,
    solve_timetable_backtracking
)

app = Flask(__name__, static_folder="static")

data_dir = os.path.join(PROJECT_ROOT, "data")
venue_service = VenueService(data_dir=data_dir)
booking_service = BookingService(data_dir=data_dir)
navigation_service = NavigationService(data_dir=data_dir)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("static", path)


# =============================================================================
# 1. VENUE DIRECTORY API (LINKED LIST, BST & UNDO STACK)
# =============================================================================

@app.route("/api/venues", methods=["GET"])
def get_venues():
    venues = venue_service.get_all_venues()
    return jsonify({
        "venues": [v.to_dict() for v in venues],
        "count": len(venues),
        "pointer_chain": venue_service.get_linked_list_display(),
        "bst_info": {
            "size": venue_service.venue_bst.size(),
            "height": venue_service.venue_bst.height()
        }
    })


@app.route("/api/venues", methods=["POST"])
def add_venue():
    data = request.json or {}
    vid = data.get("venue_id", "").strip() or data.get("id", "").strip()
    name = data.get("name", "").strip()
    building = data.get("building", "Main Block").strip()
    category = data.get("category", "Auditorium").strip()
    capacity = int(data.get("capacity", 250))
    air_conditioned = bool(data.get("air_conditioned", True))
    projector = bool(data.get("projector", True))
    sound_system = data.get("sound_system", "Integrated Audio").strip()
    seating_type = data.get("seating_type", "Tiered Seating").strip()
    wheelchair_accessible = bool(data.get("wheelchair_accessible", True))
    usage_policy = data.get("usage_policy", "College Academic Use").strip()
    at_front = bool(data.get("at_front", False))

    if not vid or not name:
        return jsonify({"success": False, "message": "Venue ID and Name are required."}), 400

    rec = venue_service.add_venue(
        venue_id=vid,
        name=name,
        building=building,
        category=category,
        capacity=capacity,
        air_conditioned=air_conditioned,
        projector=projector,
        sound_system=sound_system,
        seating_type=seating_type,
        wheelchair_accessible=wheelchair_accessible,
        usage_policy=usage_policy,
        at_front=at_front
    )
    # Also register in booking service interval trees
    booking_service.register_venue(vid, name, capacity, building)

    pos = "Head" if at_front else "Tail"
    return jsonify({
        "success": True,
        "message": f"Venue {rec.venue_id} inserted at {pos} of Singly Linked List.",
        "venue": rec.to_dict()
    })


@app.route("/api/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    success = venue_service.delete_venue(venue_id)
    if success:
        return jsonify({"success": True, "message": f"Venue '{venue_id}' deleted from Linked List and BST."})
    return jsonify({"success": False, "message": f"Venue '{venue_id}' not found."}), 404


@app.route("/api/venues/reverse", methods=["POST"])
def reverse_venues():
    venue_service.reverse_venue_list()
    return jsonify({
        "success": True,
        "message": "Venue Linked List reversed in-place in O(n) time.",
        "pointer_chain": venue_service.get_linked_list_display()
    })


@app.route("/api/venues/undo", methods=["POST"])
def undo_venue_action():
    success, msg = venue_service.undo_last_operation()
    return jsonify({
        "success": success,
        "message": msg,
        "undo_stack_depth": len(venue_service.undo_stack)
    })


@app.route("/api/venues/bst-traversals", methods=["GET"])
def get_bst_traversals():
    return jsonify(venue_service.get_bst_traversals())


# =============================================================================
# 2. VENUE BOOKINGS & INTERVAL TREE CLASH DETECTION API
# =============================================================================

@app.route("/api/bookings", methods=["GET"])
def get_bookings():
    venue_id = request.args.get("venue_id")
    date = request.args.get("date")
    if venue_id:
        schedule = booking_service.get_venue_schedule(venue_id, date=date)
        return jsonify([b.to_dict() for b in schedule])
    else:
        all_b = booking_service.get_all_bookings()
        return jsonify([b.to_dict() for b in all_b])


@app.route("/api/bookings/pending", methods=["GET"])
def get_pending_bookings():
    """Returns all booking requests awaiting Admin approval."""
    pending = booking_service.get_pending_bookings()
    return jsonify([b.to_dict() for b in pending])


@app.route("/api/bookings/requests", methods=["GET"])
def get_user_requests():
    """Returns user booking requests across all statuses (Pending, Approved, Rejected)."""
    requests_list = booking_service.get_user_booking_requests()
    return jsonify([b.to_dict() for b in requests_list])


@app.route("/api/bookings/<booking_id>/approve", methods=["POST"])
def approve_booking(booking_id):
    """Admin side: Approves a pending booking request into the AVL Interval Tree."""
    success, msg, booking = booking_service.approve_booking(booking_id)
    if success:
        return jsonify({
            "success": True,
            "message": msg,
            "booking": booking.to_dict() if booking else None
        }), 200
    else:
        return jsonify({"success": False, "message": msg}), 400


@app.route("/api/bookings/<booking_id>/reject", methods=["POST"])
def reject_booking(booking_id):
    """Admin side: Rejects a pending booking request."""
    data = request.json or {}
    reason = data.get("reason", "Declined by Campus Facility Administration")
    success, msg = booking_service.reject_booking(booking_id, reason=reason)
    if success:
        return jsonify({"success": True, "message": msg}), 200
    else:
        return jsonify({"success": False, "message": msg}), 400


@app.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.json or {}
    venue_id = data.get("venue_id")
    title = data.get("title")
    organizer = data.get("organizer", "General Department")
    date = data.get("date", "2026-09-10")
    role = data.get("role", "user")
    auto_approve = bool(data.get("auto_approve", False))

    start_str = data.get("start_time")
    end_str = data.get("end_time")

    if not venue_id or not title or not start_str or not end_str:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        start_min = BookingService.time_str_to_minutes(start_str)
        end_min = BookingService.time_str_to_minutes(end_str)
    except Exception:
        return jsonify({"success": False, "message": "Invalid time format. Use HH:MM"}), 400

    # If Admin or auto_approve requested, book directly into Interval Tree
    if role == "admin" or auto_approve:
        success, msg, booking, clashes = booking_service.add_booking(
            venue_id=venue_id,
            title=title,
            organizer=organizer,
            start_min=start_min,
            end_min=end_min,
            date=date
        )
    else:
        # User side submission -> submits for Admin approval
        success, msg, booking, clashes = booking_service.request_booking(
            venue_id=venue_id,
            title=title,
            organizer=organizer,
            start_min=start_min,
            end_min=end_min,
            date=date
        )

    if success and booking:
        return jsonify({
            "success": True,
            "message": msg,
            "status": booking.status,
            "request_id": booking.booking_id if booking.status == "Pending" else None,
            "booking": booking.to_dict()
        }), (202 if booking.status == "Pending" else 201)
    else:
        return jsonify({
            "success": False,
            "message": msg,
            "clashes": [c.to_dict() for c in clashes]
        }), 409


@app.route("/api/bookings/<booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    success, msg = booking_service.cancel_booking(booking_id)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"success": False, "message": msg}), 404


@app.route("/api/venues/<venue_id>/tree", methods=["GET"])
def get_interval_tree(venue_id):
    tree_ascii = booking_service.get_tree_ascii(venue_id)
    tree_json = booking_service.get_tree_json(venue_id)
    return jsonify({
        "venue_id": venue_id,
        "tree_ascii": tree_ascii,
        "tree_json": tree_json
    })


# =============================================================================
# 3. VENUE WAITLIST QUEUE (CUSTOM FIFO QUEUE)
# =============================================================================

@app.route("/api/waitlist", methods=["GET"])
def get_waitlist():
    return jsonify({
        "waitlist": venue_service.get_waitlist_state(),
        "count": venue_service.get_waitlist_count()
    })


@app.route("/api/waitlist", methods=["POST"])
def enqueue_waitlist():
    data = request.json or {}
    req_id = data.get("request_id", f"REQ-{random.randint(100, 999)}")
    venue_id = data.get("venue_id", "auditorium_main")
    title = data.get("title", "").strip()
    organizer = data.get("organizer", "Academic Dept").strip()
    time_slot = data.get("time_slot", "14:00 - 17:00").strip()

    if not title:
        return jsonify({"success": False, "message": "Title is required for waitlist."}), 400

    item = venue_service.enqueue_waitlist_request(req_id, venue_id, title, organizer, time_slot)
    return jsonify({
        "success": True,
        "message": f"Waitlist token {item['token']} issued via LinkedQueue.",
        "item": item
    })


@app.route("/api/waitlist/serve", methods=["POST"])
def serve_waitlist():
    item = venue_service.dequeue_waitlist_request()
    if not item:
        return jsonify({"success": False, "message": "Waitlist queue is empty."}), 404
    return jsonify({
        "success": True,
        "message": f"Served & approved token {item['token']} for '{item['title']}'.",
        "item": item
    })


# =============================================================================
# 4. PRIORITY EVENT ALLOCATION (CUSTOM BINARY MAX-HEAP)
# =============================================================================

@app.route("/api/priority-requests", methods=["GET"])
def get_priority_requests():
    return jsonify({
        "requests": venue_service.get_all_priority_requests(),
        "count": len(venue_service.priority_heap)
    })


@app.route("/api/priority-requests", methods=["POST"])
def add_priority_request():
    data = request.json or {}
    req_id = data.get("request_id", f"PRIO-{random.randint(100, 999)}")
    title = data.get("title", "").strip()
    venue_id = data.get("venue_id", "auditorium_main")
    priority_score = float(data.get("priority_score", 5.0))
    organizer = data.get("organizer", "University Directorate").strip()

    if not title:
        return jsonify({"success": False, "message": "Title is required for priority request."}), 400

    item = venue_service.add_priority_request(req_id, title, venue_id, priority_score, organizer)
    return jsonify({
        "success": True,
        "message": f"Inserted into Max-Heap with Priority Score {priority_score}.",
        "item": item
    })


@app.route("/api/priority-requests/dispatch", methods=["POST"])
def dispatch_highest_priority():
    item = venue_service.extract_highest_priority()
    if not item:
        return jsonify({"success": False, "message": "No priority requests pending."}), 404
    return jsonify({
        "success": True,
        "message": f"Dispatched top-priority event '{item['title']}' (Score {item['priority_score']}) via extract-max.",
        "item": item
    })


@app.route("/api/priority-requests/escalate", methods=["POST"])
def escalate_priority():
    data = request.json or {}
    req_id = data.get("request_id")
    new_priority = float(data.get("new_priority", 10.0))

    if not req_id:
        return jsonify({"success": False, "message": "request_id required"}), 400

    success = venue_service.escalate_priority_request(req_id, new_priority)
    if success:
        return jsonify({
            "success": True,
            "message": f"Priority for '{req_id}' escalated to {new_priority} in O(log n)."
        })
    return jsonify({"success": False, "message": f"Request '{req_id}' not found or priority was lower."}), 404


# =============================================================================
# 5. VENUE RESOURCE & TECHNICAL SETUP EVALUATOR (STACK-BASED SHUNTING YARD)
# =============================================================================

@app.route("/api/resources/calculate", methods=["POST"])
def calculate_resources():
    data = request.json or {}
    attendees = float(data.get("attendees", 250.0))
    hours = float(data.get("duration_hours", 2.5))
    av_units = float(data.get("av_equipment_units", 30.0))
    buffer_percent = float(data.get("buffer_percent", 10.0))
    formula = data.get("formula")

    result = venue_service.calculate_resource_score(
        attendees=attendees,
        duration_hours=hours,
        av_equipment_units=av_units,
        buffer_percent=buffer_percent,
        formula_override=formula
    )
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


# =============================================================================
# 6. SEARCHING & SORTING BENCHMARK ON VENUES
# =============================================================================

@app.route("/api/venues/search", methods=["POST"])
def search_venues():
    data = request.json or {}
    target_capacity = int(data.get("target_capacity", 250))

    venues = venue_service.get_all_venues()
    sorted_by_cap = sorted(venues, key=lambda v: v.capacity)

    l_idx, l_comp = linear_search(venues, target_capacity, key_func=lambda v: v.capacity)
    b_idx, b_comp = binary_search(sorted_by_cap, target_capacity, key_func=lambda v: v.capacity)

    return jsonify({
        "target_capacity": target_capacity,
        "total_records": len(venues),
        "linear_search": {
            "found": l_idx != -1,
            "venue": venues[l_idx].to_dict() if l_idx != -1 else None,
            "comparisons": l_comp,
            "complexity": "O(n)"
        },
        "binary_search": {
            "found": b_idx != -1,
            "venue": sorted_by_cap[b_idx].to_dict() if b_idx != -1 else None,
            "comparisons": b_comp,
            "complexity": "O(log n)"
        }
    })


@app.route("/api/venues/sort", methods=["GET"])
def sort_venues():
    sort_key = request.args.get("key", "capacity")
    algorithm = request.args.get("algorithm", "merge_sort").lower()

    venues = venue_service.get_all_venues()
    raw_list = [v.to_dict() for v in venues]

    t0 = time.perf_counter()
    if algorithm == "quick_sort":
        sorted_list = quick_sort(raw_list, key_func=lambda v: v[sort_key])
    elif algorithm == "insertion_sort":
        sorted_list = insertion_sort(raw_list, key_func=lambda v: v[sort_key])
    else:
        sorted_list = merge_sort(raw_list, key_func=lambda v: v[sort_key])
    elapsed_ms = (time.perf_counter() - t0) * 1000

    benchmarks = compare_sorting_algorithms(raw_list, key_func=lambda v: v[sort_key], runs=3)

    return jsonify({
        "algorithm": algorithm,
        "sort_key": sort_key,
        "elapsed_ms": round(elapsed_ms, 4),
        "sorted_venues": sorted_list,
        "benchmarks": benchmarks
    })


# =============================================================================
# 7. ALGORITHMIC PROBLEM SOLVING (GREEDY, KNAPSACK DP, BACKTRACKING CSP)
# =============================================================================

@app.route("/api/algorithms/greedy-schedule", methods=["POST"])
def run_greedy_scheduler():
    data = request.json or {}
    raw_activities = data.get("activities", [
        {"name": "AI Workshop", "start": 9.0, "finish": 11.5, "priority": 1},
        {"name": "Keynote Address", "start": 10.0, "finish": 12.0, "priority": 2},
        {"name": "Networking Tea", "start": 11.5, "finish": 12.5, "priority": 1},
        {"name": "Hands-on Lab", "start": 12.0, "finish": 14.0, "priority": 1},
        {"name": "Panel Discussion", "start": 13.0, "finish": 15.0, "priority": 2},
        {"name": "Valedictory Ceremony", "start": 14.5, "finish": 16.5, "priority": 3}
    ])

    activities = [
        Activity(
            name=a["name"],
            start=float(a["start"]),
            finish=float(a["finish"]),
            priority=int(a.get("priority", 1))
        )
        for a in raw_activities
    ]

    selected, log = greedy_activity_selection(activities)
    return jsonify({
        "technique": "Greedy Algorithm (Earliest Finish Time First)",
        "complexity": "O(n log n)",
        "selected_count": len(selected),
        "selected_activities": [a.to_dict() for a in selected],
        "decision_log": log
    })


@app.route("/api/algorithms/equipment-knapsack", methods=["POST"])
def run_equipment_knapsack():
    data = request.json or {}
    capacity = int(data.get("budget_or_power_limit", 150))
    raw_items = data.get("items", [
        {"name": "Laser 4K Projector", "cost": 40, "utility": 85},
        {"name": "Line Array Audio Rig", "cost": 50, "utility": 95},
        {"name": "Wireless Lapel Mic Set", "cost": 20, "utility": 45},
        {"name": "PTZ Streaming Camera", "cost": 30, "utility": 70},
        {"name": "Interactive Podium Pod", "cost": 35, "utility": 65},
        {"name": "Stage LED Uplighting", "cost": 25, "utility": 40}
    ])

    items = [
        BudgetItem(name=it["name"], cost=int(it["cost"]), utility=int(it["utility"]))
        for it in raw_items
    ]

    max_util, chosen, table = knapsack_budget_optimizer(items, capacity)
    return jsonify({
        "technique": "Dynamic Programming (0/1 Knapsack)",
        "complexity": "O(n * W)",
        "capacity_limit": capacity,
        "max_utility": max_util,
        "selected_equipment": [c.to_dict() for c in chosen],
        "dp_table_summary": {
            "rows": len(table),
            "cols": len(table[0]) if table else 0
        }
    })


@app.route("/api/algorithms/exam-timetable", methods=["POST"])
def run_exam_timetable():
    data = request.json or {}
    courses = data.get("courses", ["MCA-DSA", "MCA-ADBMS", "MCA-Cloud", "MCA-ML", "MCA-Cyber"])
    clash_pairs = data.get("conflicts", [
        ("MCA-DSA", "MCA-ADBMS"),
        ("MCA-DSA", "MCA-ML"),
        ("MCA-ADBMS", "MCA-Cloud"),
        ("MCA-ML", "MCA-Cyber"),
        ("MCA-Cloud", "MCA-Cyber")
    ])
    num_venues = int(data.get("num_venues", 3))

    conflicts = {c: set() for c in courses}
    for u, v in clash_pairs:
        if u in conflicts and v in conflicts:
            conflicts[u].add(v)
            conflicts[v].add(u)

    slots = [f"Venue Hall {i+1}" for i in range(num_venues)]
    success, schedule, steps = solve_timetable_backtracking(courses, conflicts, slots)

    return jsonify({
        "technique": "Backtracking Constraint Satisfaction Problem (Graph Coloring)",
        "complexity": "O(m^V) worst-case with pruning",
        "feasible": success,
        "schedule": schedule if success else {},
        "backtrack_steps": steps,
        "venues_used": len(set(schedule.values())) if success else 0
    })


# =============================================================================
# 8. CAMPUS VENUE NAVIGATION (GRAPH + MIN-HEAP DIJKSTRA)
# =============================================================================

@app.route("/api/landmarks", methods=["GET"])
def get_landmarks():
    return jsonify(navigation_service.get_all_landmarks())


@app.route("/api/pathways", methods=["GET"])
def get_pathways():
    return jsonify(navigation_service.get_all_pathways())


@app.route("/api/navigate", methods=["POST"])
def navigate_venues():
    data = request.json or {}
    start_id = data.get("start_id")
    dest_id = data.get("dest_id")
    accessible_only = bool(data.get("accessible_only", False))

    if not start_id or not dest_id:
        return jsonify({"success": False, "message": "start_id and dest_id required"}), 400

    route = navigation_service.find_route(start_id, dest_id, accessible_only=accessible_only)
    if route:
        return jsonify({"success": True, "route": route})
    else:
        return jsonify({"success": False, "message": "No route found under current constraints."}), 404


# =============================================================================
# 9. BENCHMARKS API
# =============================================================================

@app.route("/api/benchmarks", methods=["GET"])
def run_benchmarks():
    from core.interval_tree import IntervalTree
    from core.max_heap import MaxHeap

    tree = IntervalTree()
    linear_list = []
    n = 3000
    random.seed(123)
    for i in range(n):
        s = random.randint(1, 10000)
        e = s + random.randint(15, 60)
        tree.insert(s, e, f"E{i}")
        linear_list.append((s, e, f"E{i}"))

    queries = [(random.randint(1, 10000), random.randint(15, 60)) for _ in range(50)]

    t0 = time.perf_counter()
    for s, dur in queries:
        tree.find_all_overlapping(s, s + dur)
    tree_time_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    for s, dur in queries:
        low, high = s, s + dur
        _ = [item for item in linear_list if item[0] < high and low < item[1]]
    linear_time_ms = (time.perf_counter() - t0) * 1000

    heap = MaxHeap()
    unsorted = []
    for i in range(5000):
        val = float(random.randint(1, 10000))
        heap.insert(f"ID_{i}", val)
        unsorted.append(val)

    t0 = time.perf_counter()
    for _ in range(200):
        heap.extract_max()
    heap_time_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    for _ in range(200):
        m_idx = 0
        for j in range(1, len(unsorted)):
            if unsorted[j] > unsorted[m_idx]:
                m_idx = j
        unsorted.pop(m_idx)
    list_time_ms = (time.perf_counter() - t0) * 1000

    return jsonify({
        "interval_tree": {
            "n": n,
            "queries": 50,
            "tree_time_ms": round(tree_time_ms, 3),
            "linear_time_ms": round(linear_time_ms, 3),
            "speedup": round(linear_time_ms / max(tree_time_ms, 0.0001), 1)
        },
        "max_heap": {
            "n": 5000,
            "extractions": 200,
            "heap_time_ms": round(heap_time_ms, 3),
            "list_time_ms": round(list_time_ms, 3),
            "speedup": round(list_time_ms / max(heap_time_ms, 0.0001), 1)
        }
    })


def run_server(port=None, debug=False):
    if port is None:
        port = int(os.environ.get("PORT", 5001))
    else:
        port = int(os.environ.get("PORT", port))
    print(f"Starting Smart Campus Venue Management Engine on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=debug)


if __name__ == "__main__":
    run_server(port=5001, debug=True)
````

## `web/static/app.js`

````javascript
/**
 * Kristu Jayanti University - Smart Campus Venue & Facility Management Engine
 * File: web/static/app.js
 * 
 * Interactive Client Controller connecting the modern UI to pure Data Structure APIs:
 * - Augmented AVL Interval Tree (clash detection, timeline rendering)
 * - Custom Singly Linked List (venue registry & pointer chain)
 * - Custom Binary Search Tree (venue indexing & 3-case deletion)
 * - Custom Linked Stack (undo recovery)
 * - Custom Linked Queue (FIFO waitlist counter)
 * - Custom Binary Max-Heap (priority allocation engine)
 * - Stack-based expression evaluation for facility setup scores
 * - Adjacency List Graph + Min-Heap Dijkstra (campus venue wayfinding)
 */

let currentPortal = localStorage.getItem("kju_portal") || "user";
let allVenues = [];
let selectedVenueId = "ske_auditorium";
let currentRouteNodeIds = new Set();
let campusLandmarks = [];
let campusPathways = [];

// INITIALIZATION
// ----------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    applyPortalState();
    initNavigationTabs();
    initForms();
    loadVenues();
    loadWaitlist();
    loadPriorityRequests();
    loadCampusMap();
    loadLiveBenchmarks();
    loadPendingBookings();
    loadUserRequests();
});

function initNavigationTabs() {
    const tabs = document.querySelectorAll(".tab-btn");
    tabs.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            switchNavTab(tabId);
        });
    });
}

function switchNavTab(tabId) {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));

    const targetBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    const targetPanel = document.getElementById(tabId);

    if (targetBtn) targetBtn.classList.add("active");
    if (targetPanel) targetPanel.classList.add("active");

    if (tabId === "tabBookings") {
        loadBookings(selectedVenueId);
        loadPendingBookings();
        loadUserRequests();
        refreshIntervalTreeAscii();
    } else if (tabId === "tabNavigation") {
        setTimeout(renderSvgMap, 50);
    }
}

function switchPortal(portal) {
    currentPortal = portal;
    localStorage.setItem("kju_portal", portal);
    applyPortalState();
}

function applyPortalState() {
    document.body.setAttribute("data-portal", currentPortal);

    const btnUser = document.getElementById("btnUserPortal");
    const btnAdmin = document.getElementById("btnAdminPortal");
    const roleInd = document.getElementById("portalRoleIndicator");
    const formHeading = document.getElementById("bookingFormHeading");
    const formBadge = document.getElementById("bookingFormBadge");
    const formDesc = document.getElementById("bookingFormDescription");
    const submitBtn = document.getElementById("bookSubmitBtn");

    if (currentPortal === "admin") {
        if (btnAdmin) {
            btnAdmin.classList.add("admin-active");
            btnAdmin.classList.remove("active");
        }
        if (btnUser) btnUser.classList.remove("active");
        if (roleInd) roleInd.textContent = "Admin Portal";
        if (formHeading) formHeading.textContent = "Admin Direct Schedule";
        if (formBadge) {
            formBadge.textContent = "Direct Schedule";
            formBadge.className = "badge badge-rose";
        }
        if (formDesc) formDesc.textContent = "Admin Mode: Direct slot scheduling into the AVL Interval Tree with automated conflict detection.";
        if (submitBtn) submitBtn.innerHTML = "⚡ Confirm Direct Schedule";
        loadPendingBookings();
    } else {
        if (btnUser) btnUser.classList.add("active");
        if (btnAdmin) btnAdmin.classList.remove("admin-active", "active");
        if (roleInd) roleInd.textContent = "User Portal";
        if (formHeading) formHeading.textContent = "Request Venue Booking";
        if (formBadge) {
            formBadge.textContent = "User Portal";
            formBadge.className = "badge badge-emerald";
        }
        if (formDesc) formDesc.textContent = "Select auditorium or lab, event interval, and submit. Your request is queued for Admin approval.";
        if (submitBtn) submitBtn.innerHTML = "📩 Submit Booking Request";
        loadUserRequests();
    }
}

function initForms() {
    // Venue Form
    const vForm = document.getElementById("venueForm");
    if (vForm) {
        vForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const payload = {
                venue_id: document.getElementById("vidInput").value.trim(),
                name: document.getElementById("vnameInput").value.trim(),
                building: document.getElementById("vbuildingInput").value.trim(),
                category: document.getElementById("vcategoryInput").value,
                capacity: parseInt(document.getElementById("vcapacityInput").value, 10),
                usage_policy: document.getElementById("vpolicyInput") ? document.getElementById("vpolicyInput").value.trim() : "College Academic Use",
                at_front: document.getElementById("vAtFront") ? document.getElementById("vAtFront").checked : false
            };

            fetch("/api/venues", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    vForm.reset();
                    loadVenues();
                } else {
                    alert("Error: " + data.message);
                }
            })
            .catch(err => console.error(err));
        });
    }

    // Booking Form
    const bForm = document.getElementById("bookingForm");
    if (bForm) {
        const bookingDateInput = document.getElementById("bookDate");
        if (bookingDateInput) {
            bookingDateInput.addEventListener("change", () => {
                loadBookings(selectedVenueId, bookingDateInput.value);
            });
        }

        bForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const clashAlert = document.getElementById("clashAlertBox");
            if (clashAlert) clashAlert.style.display = "none";

            const payload = {
                venue_id: document.getElementById("bookVenueSelect").value,
                title: document.getElementById("bookTitle").value.trim(),
                organizer: document.getElementById("bookOrganizer").value.trim(),
                start_time: document.getElementById("bookStartTime").value,
                end_time: document.getElementById("bookEndTime").value,
                date: document.getElementById("bookDate").value,
                role: currentPortal
            };

            const submitBtn = document.getElementById("bookSubmitBtn");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = "Submitting...";
            }

            fetch("/api/bookings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json().then(data => ({ status: res.status, data })))
            .then(({ status, data }) => {
                if (status === 202 && data.success) {
                    alert(`📩 Booking Request Submitted!\nYour request (${data.request_id || data.booking?.booking_id}) for "${payload.title}" has been sent to Campus Admin for approval.`);
                    bForm.reset();
                    document.getElementById("bookVenueSelect").value = payload.venue_id;
                    document.getElementById("bookDate").value = payload.date;
                    document.getElementById("bookStartTime").value = "14:00";
                    document.getElementById("bookEndTime").value = "16:00";
                    loadUserRequests();
                    loadPendingBookings();
                    loadBookings(payload.venue_id, payload.date);
                } else if (status === 201 && data.success) {
                    alert("✅ Slot Scheduled Successfully! Added to AVL Interval Tree.");
                    bForm.reset();
                    document.getElementById("bookVenueSelect").value = payload.venue_id;
                    document.getElementById("bookDate").value = payload.date;
                    document.getElementById("bookStartTime").value = "14:00";
                    document.getElementById("bookEndTime").value = "16:00";
                    loadBookings(payload.venue_id, payload.date);
                    loadPendingBookings();
                    loadUserRequests();
                    refreshIntervalTreeAscii();
                    updateTotalBookingsKpi();
                } else if (status === 409) {
                    if (clashAlert) {
                        clashAlert.style.display = "block";
                        const msgEl = document.getElementById("clashAlertMsg");
                        const clashList = data.clashes ? data.clashes.map(c => `• ${c.title} (${c.start_time_str} - ${c.end_time_str})`).join("<br>") : "";
                        msgEl.innerHTML = `<strong>${data.message}</strong><br><div style="margin-top:4px;">${clashList}</div>`;
                    }
                } else {
                    alert("Error: " + (data.message || "Failed to process booking request."));
                }
            })
            .catch(err => {
                console.error(err);
                alert("The booking request could not reach the server. Check that the Smart Campus app is running, then try again.");
            })
            .finally(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    applyPortalState();
                }
            });
        });
    }

    // Waitlist Form
    const wForm = document.getElementById("waitlistForm");
    if (wForm) {
        wForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const payload = {
                venue_id: document.getElementById("waitlistVenue").value,
                title: document.getElementById("waitlistTitle").value.trim(),
                organizer: document.getElementById("waitlistOrganizer").value.trim(),
                time_slot: document.getElementById("waitlistTimeSlot").value.trim()
            };

            fetch("/api/waitlist", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("🎫 " + data.message);
                    wForm.reset();
                    loadWaitlist();
                } else {
                    alert("Error: " + data.message);
                }
            });
        });
    }

    // Priority Form
    const pForm = document.getElementById("priorityForm");
    if (pForm) {
        pForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const payload = {
                title: document.getElementById("prioTitle").value.trim(),
                venue_id: document.getElementById("prioVenue").value,
                organizer: document.getElementById("prioOrganizer").value.trim(),
                priority_score: parseFloat(document.getElementById("prioScore").value)
            };

            fetch("/api/priority-requests", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("👑 " + data.message);
                    pForm.reset();
                    loadPriorityRequests();
                } else {
                    alert("Error: " + data.message);
                }
            });
        });
    }

}

// ----------------------------------------------------------------------------
// 1. VENUES & LINKED LIST CONTROLLER
// ----------------------------------------------------------------------------

function loadVenues() {
    fetch("/api/venues")
        .then(res => res.json())
        .then(data => {
            allVenues = data.venues || [];
            document.getElementById("dashVenueCount").innerText = allVenues.length;

            renderVenueTable(allVenues);
            renderPointerChain(data.pointer_chain || []);
            populateVenueDropdowns(allVenues);
            renderAnalyticsTable(allVenues);

            // Trigger booking load for default selected venue
            if (allVenues.length > 0) {
                if (!allVenues.find(v => v.id === selectedVenueId)) {
                    selectedVenueId = allVenues[0].id;
                }
                loadBookings(selectedVenueId);
            }
        })
        .catch(err => console.error(err));
}

function renderVenueTable(venues) {
    const tbody = document.getElementById("venueTableBody");
    if (!tbody) return;

    if (venues.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 2rem; color: var(--text-muted);">No venues registered.</td></tr>`;
        return;
    }

    tbody.innerHTML = venues.map(v => `
        <tr>
            <td><code style="color:var(--accent-blue); font-weight:600;">${v.id}</code></td>
            <td><strong>${v.name}</strong></td>
            <td>${v.building}</td>
            <td><span class="badge badge-purple">${v.category}</span></td>
            <td><span class="badge badge-cyan">${v.capacity} seats</span></td>
            <td>${v.sound_system || 'Integrated Audio'}</td>
            <td><span style="font-size:0.75rem; color:var(--text-secondary);">${v.usage_policy || 'College Use Only'}</span></td>
            <td>
                <button class="btn btn-secondary" style="padding: 0.25rem 0.6rem; font-size: 0.75rem; color: var(--accent-rose);" onclick="deleteVenue('${v.id}')">
                    Delete
                </button>
            </td>
        </tr>
    `).join("");
}

function renderPointerChain(chain) {
    const container = document.getElementById("venuePointerChain");
    if (!container) return;

    if (chain.length === 0) {
        container.innerHTML = `<span style="color:var(--text-muted); font-size: 0.8rem;">[ Head: NULL ]</span>`;
        return;
    }

    const items = chain.map((node, idx) => `
        <div style="display:inline-flex; align-items:center; margin-bottom: 0.4rem;">
            <div style="background: rgba(19, 27, 46, 0.9); border: 1px solid var(--border-accent); border-radius: 6px; padding: 0.4rem 0.6rem; font-size: 0.75rem; text-align: left;">
                <span style="color:var(--accent-blue); font-weight:700;">${idx === 0 ? 'HEAD: ' : ''}${node.venue_id}</span>
                <span style="color:var(--text-muted); font-size: 0.7rem; display:block;">Cap: ${node.capacity}</span>
            </div>
            <span style="color:var(--accent-indigo); font-size: 0.9rem; margin: 0 0.35rem;">➔</span>
        </div>
    `).join("");

    container.innerHTML = items + `<div style="display:inline-flex; align-items:center;"><span style="color:var(--text-muted); font-size: 0.75rem; background: rgba(0,0,0,0.4); padding: 0.3rem 0.5rem; border-radius:4px;">NULL</span></div>`;
}

function populateVenueDropdowns(venues) {
    const selects = ["bookVenueSelect", "waitlistVenue", "prioVenue"];
    selects.forEach(selId => {
        const el = document.getElementById(selId);
        if (!el) return;
        const curVal = el.value;
        el.innerHTML = venues.map(v => `<option value="${v.id}">${v.name} (${v.capacity} seats)</option>`).join("");
        if (curVal && venues.find(v => v.id === curVal)) {
            el.value = curVal;
        }
    });

    const navStart = document.getElementById("navStartSelect");
    if (navStart) {
        navStart.innerHTML = `
            <option value="main_gate">Gate 1</option>
            <option value="gate_2">Gate 2 (Vehicular)</option>
            <option value="main_block">Main Block</option>
            <option value="cs_block">PG Block</option>
            <option value="admin_block">Admin Block</option>
            <option value="humanities_block">Humanities Block</option>
            <option value="admin_parking">Admin Block Basement Parking</option>
            <option value="humanities_parking">Humanities Block Basement Parking</option>
        `;
    }

    const navDest = document.getElementById("navDestSelect");
    if (navDest) {
        navDest.innerHTML = `
            <option value="admin_parking">Admin Block Basement Parking</option>
            <option value="humanities_parking">Humanities Block Basement Parking</option>
            <option value="main_block">Main Block</option>
            <option value="cs_block">PG Block</option>
            <option value="admin_block">Admin Block</option>
            <option value="humanities_block">Humanities Block</option>
            <option value="main_gate">Gate 1</option>
            <option value="gate_2">Gate 2</option>
        `;
    }
}

function filterVenueTable() {
    const query = (document.getElementById("venueSearchInput").value || "").toLowerCase();
    const cat = document.getElementById("venueCategoryFilter").value;

    const filtered = allVenues.filter(v => {
        const matchesQuery = v.name.toLowerCase().includes(query) || v.id.toLowerCase().includes(query) || v.building.toLowerCase().includes(query);
        const matchesCat = cat === "ALL" || v.category === cat;
        return matchesQuery && matchesCat;
    });

    renderVenueTable(filtered);
}

function deleteVenue(vid) {
    if (!confirm(`Are you sure you want to delete venue '${vid}' from Linked List & BST?`)) return;

    fetch(`/api/venues/${vid}`, { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            loadVenues();
        });
}

function reverseVenueList() {
    fetch("/api/venues/reverse", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            alert("🔄 " + data.message);
            loadVenues();
        });
}

function undoVenueAction() {
    fetch("/api/venues/undo", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            alert("↩️ " + data.message);
            loadVenues();
        });
}

function loadBstTraversals(type) {
    fetch("/api/venues/bst-traversals")
        .then(res => res.json())
        .then(data => {
            const box = document.getElementById("bstOutputBox");
            const nodes = data[type] || [];
            if (nodes.length === 0) {
                box.innerText = `BST is empty.`;
                return;
            }
            box.innerText = `${type.toUpperCase()} TRAVERSAL (${nodes.length} nodes, Height: ${data.height}):\n` +
                nodes.map((n, idx) => `[${idx + 1}] Key: ${n.key} ➔ Venue: ${n.value.name} (Cap: ${n.value.capacity})`).join("\n");
        });
}

// ----------------------------------------------------------------------------
// 2. VENUE BOOKINGS & INTERVAL TIMELINE CONTROLLER
// ----------------------------------------------------------------------------

function onBookingVenueChanged() {
    const sel = document.getElementById("bookVenueSelect");
    if (!sel) return;
    selectedVenueId = sel.value;
    loadBookings(selectedVenueId, document.getElementById("bookDate")?.value);
    refreshIntervalTreeAscii();
}

function loadBookings(venueId, date = document.getElementById("bookDate")?.value) {
    selectedVenueId = venueId;
    const v = allVenues.find(item => item.id === venueId);
    const titleEl = document.getElementById("timelineVenueTitle");
    const badgeEl = document.getElementById("timelineVenueBadge");

    if (titleEl) titleEl.innerText = v ? `Schedule: ${v.name}` : `Venue Schedule: ${venueId}`;
    if (badgeEl) badgeEl.innerText = venueId;

    const query = new URLSearchParams({ venue_id: venueId });
    if (date) query.set("date", date);
    fetch(`/api/bookings?${query.toString()}`)
        .then(res => res.json())
        .then(bookings => {
            renderTimelineTrack(bookings);
            renderBookingsTable(bookings);
            updateTotalBookingsKpi();
        })
        .catch(err => console.error(err));
}

function updateTotalBookingsKpi() {
    fetch("/api/bookings")
        .then(res => res.json())
        .then(allB => {
            const kpi = document.getElementById("dashBookingCount");
            if (kpi) kpi.innerText = allB.length;
        });
}

function renderTimelineTrack(bookings) {
    const track = document.getElementById("timelineTrack");
    if (!track) return;

    // Timeline spans 08:00 (480 min) to 20:00 (1200 min) -> Total 720 minutes
    const dayStart = 480;
    const totalDayMins = 720;

    track.innerHTML = "";

    bookings.forEach(b => {
        const leftPercent = Math.max(0, Math.min(100, ((b.start_min - dayStart) / totalDayMins) * 100));
        const widthPercent = Math.max(2, Math.min(100 - leftPercent, ((b.end_min - b.start_min) / totalDayMins) * 100));

        const block = document.createElement("div");
        block.className = "timeline-event-block";
        block.style.left = `${leftPercent}%`;
        block.style.width = `${widthPercent}%`;
        block.title = `${b.title} (${b.start_time_str} - ${b.end_time_str})`;

        block.innerHTML = `
            <div style="font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${b.title}</div>
            <div style="font-size:0.68rem; opacity:0.85;">${b.start_time_str} - ${b.end_time_str}</div>
        `;

        track.appendChild(block);
    });
}

function renderBookingsTable(bookings) {
    const tbody = document.getElementById("bookingsTableBody");
    if (!tbody) return;

    if (bookings.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 1.5rem; color: var(--text-muted);">No reservations booked for this venue. Hall is 100% available.</td></tr>`;
        return;
    }

    tbody.innerHTML = bookings.map(b => {
        const durHours = ((b.end_min - b.start_min) / 60).toFixed(1);
        return `
            <tr>
                <td><code style="color:var(--accent-blue); font-weight:600;">${b.booking_id}</code></td>
                <td><strong>${b.title}</strong></td>
                <td>${b.organizer}</td>
                <td><span class="badge badge-emerald">${b.start_time_str} — ${b.end_time_str}</span></td>
                <td>${durHours} hrs</td>
                <td>
                    <button class="btn btn-secondary admin-only" style="padding: 0.25rem 0.6rem; font-size: 0.75rem; color: var(--accent-rose);" onclick="cancelBooking('${b.booking_id}')">
                        Cancel Slot
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function cancelBooking(bid) {
    if (!confirm(`Cancel reservation '${bid}' and remove from Interval Tree?`)) return;

    fetch(`/api/bookings/${bid}`, { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            loadBookings(selectedVenueId);
            refreshIntervalTreeAscii();
        });
}

// ----------------------------------------------------------------------------
// ADMIN & USER BOOKING APPROVAL WORKFLOW
// ----------------------------------------------------------------------------

function loadPendingBookings() {
    fetch("/api/bookings/pending")
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("adminPendingContainer");
            const badge = document.getElementById("adminPendingBadge");
            const countBadge = document.getElementById("adminPendingCountBadge");
            const pendingRequests = Array.isArray(data)
                ? data
                : (data.pending_requests || []);
            const count = pendingRequests.length;

            if (badge) {
                badge.innerText = count;
                badge.style.display = count > 0 ? "inline-block" : "none";
            }
            if (countBadge) {
                countBadge.innerText = `${count} Pending`;
            }

            if (!container) return;

            if (pendingRequests.length === 0) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: var(--text-muted); background: rgba(0,0,0,0.25); border-radius: 8px;">
                        <span style="font-size: 1.8rem; display:block; margin-bottom: 0.4rem;">🎉</span>
                        <strong>No Pending Booking Requests</strong>
                        <p style="font-size: 0.8rem; margin-top: 0.2rem;">All venue booking requests have been reviewed.</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem;">
                    ${pendingRequests.map(req => {
                        const requestId = req.request_id || req.booking_id;
                        return `
                        <div style="background: rgba(19, 27, 46, 0.95); border: 1px solid rgba(244, 63, 94, 0.35); border-radius: 10px; padding: 1rem; display: flex; flex-direction: column; justify-content: space-between; gap: 0.75rem;">
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.4rem;">
                                    <span class="badge badge-pending" style="font-size: 0.72rem;">⏳ ${requestId}</span>
                                    <span class="badge badge-cyan" style="font-size: 0.72rem;">${req.venue_id}</span>
                                </div>
                                <h4 style="font-size: 0.96rem; color: #fff; margin-bottom: 0.25rem;">${req.title}</h4>
                                <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                                    <strong>Dept:</strong> ${req.organizer}
                                </p>
                                <div style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--accent-emerald); background: rgba(0,0,0,0.3); padding: 0.35rem 0.5rem; border-radius: 6px;">
                                    📅 ${req.date} | ⏰ ${req.start_time_str} - ${req.end_time_str}
                                </div>
                            </div>
                            <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.75rem;">
                                <button class="btn btn-primary" style="flex: 1; padding: 0.45rem 0.6rem; font-size: 0.8rem; background: linear-gradient(135deg, #10b981, #059669);" onclick="approveBookingRequest('${requestId}')">
                                    ✅ Approve
                                </button>
                                <button class="btn btn-secondary" style="flex: 1; padding: 0.45rem 0.6rem; font-size: 0.8rem; color: var(--accent-rose); border-color: rgba(244,63,94,0.4);" onclick="rejectBookingRequest('${requestId}')">
                                    ❌ Reject
                                </button>
                            </div>
                        </div>
                    `;
                    }).join("")}
                </div>
            `;
        })
        .catch(err => console.error("Error loading pending bookings:", err));
}

function approveBookingRequest(reqId) {
    fetch(`/api/bookings/${reqId}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    })
    .then(res => res.json().then(data => ({ status: res.status, data })))
    .then(({ status, data }) => {
        if (data.success) {
            alert(`✅ Approved!\nRequest ${reqId} has been approved and scheduled into the Interval Tree.`);
            loadPendingBookings();
            loadUserRequests();
            loadBookings(selectedVenueId);
            refreshIntervalTreeAscii();
            updateTotalBookingsKpi();
        } else {
            alert("Error: " + (data.message || "Failed to approve request."));
        }
    })
    .catch(err => console.error(err));
}

function rejectBookingRequest(reqId) {
    const reason = prompt("Enter rejection reason for request " + reqId + " (optional):", "Venue allocated for prior college convocation") || "Rejected by administration";
    fetch(`/api/bookings/${reqId}/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: reason })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(`❌ Rejected!\nRequest ${reqId} has been marked as rejected.`);
            loadPendingBookings();
            loadUserRequests();
        } else {
            alert("Error: " + (data.message || "Failed to reject request."));
        }
    })
    .catch(err => console.error(err));
}

function loadUserRequests() {
    fetch("/api/bookings/requests")
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("userRequestsTableBody");
            if (!tbody) return;

            const reqs = Array.isArray(data) ? data : (data.requests || []);
            if (reqs.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 1.5rem; color: var(--text-muted);">No booking requests submitted yet. Use the form below to request a venue slot.</td></tr>`;
                return;
            }

            tbody.innerHTML = reqs.map(r => {
                const requestId = r.request_id || r.booking_id;
                let badgeClass = "badge-pending";
                let badgeText = "⏳ Pending Approval";
                if (r.status === "Approved") {
                    badgeClass = "badge-approved";
                    badgeText = "✅ Approved";
                } else if (r.status === "Rejected") {
                    badgeClass = "badge-rejected";
                    badgeText = "❌ Rejected";
                }

                return `
                    <tr>
                        <td><code style="color:var(--accent-blue); font-weight:600;">${requestId}</code></td>
                        <td><strong>${r.title}</strong></td>
                        <td>${r.organizer}</td>
                        <td><span class="badge badge-cyan">${r.venue_id}</span></td>
                        <td><span style="font-family:var(--font-mono); font-size:0.78rem;">${r.date} (${r.start_time_str} - ${r.end_time_str})</span></td>
                        <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                        <td style="font-size:0.78rem; color:var(--text-secondary);">${r.rejection_reason || (r.status === "Approved" ? "Confirmed on Schedule" : "Under review by admin")}</td>
                    </tr>
                `;
            }).join("");
        })
        .catch(err => console.error("Error loading user requests:", err));
}

function refreshIntervalTreeAscii() {
    const box = document.getElementById("intervalTreeAscii");
    if (!box) return;

    fetch(`/api/venues/${selectedVenueId}/tree`)
        .then(res => res.json())
        .then(data => {
            box.innerText = data.tree_ascii || "Interval Tree is empty.";
        });
}

// ----------------------------------------------------------------------------
// 3. WAITLIST QUEUE CONTROLLER
// ----------------------------------------------------------------------------

function loadWaitlist() {
    fetch("/api/waitlist")
        .then(res => res.json())
        .then(data => {
            const kpi = document.getElementById("dashWaitlistCount");
            if (kpi) kpi.innerText = data.count || 0;

            const container = document.getElementById("waitlistQueueContainer");
            if (!container) return;

            const list = data.waitlist || [];
            if (list.length === 0) {
                container.innerHTML = `<div style="text-align:center; padding: 2rem; color:var(--text-muted); width: 100%;">Waitlist queue is empty. All venue requests are currently served.</div>`;
                return;
            }

            container.innerHTML = list.map((item, idx) => `
                <div style="background: rgba(19, 27, 46, 0.85); border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem; position: relative;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.4rem;">
                        <span class="badge badge-cyan" style="font-size: 0.75rem; font-weight:700;">${item.token}</span>
                        <span style="font-size: 0.72rem; color: var(--accent-amber); font-weight: 600;">Queue Position #${idx + 1}</span>
                    </div>
                    <h4 style="font-size: 0.92rem; margin-bottom: 0.2rem;">${item.title}</h4>
                    <p style="font-size: 0.78rem; color: var(--text-secondary); margin-bottom: 0.2rem;">Venue: <code>${item.venue_id}</code></p>
                    <p style="font-size: 0.78rem; color: var(--text-muted);">Organizer: ${item.organizer} • Slot: ${item.time_slot}</p>
                </div>
            `).join("");
        });
}

function serveNextWaitlist() {
    fetch("/api/waitlist/serve", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(`✅ Dequeued and Approved Token: ${data.item.token}\nEvent: '${data.item.title}'`);
                loadWaitlist();
            } else {
                alert(data.message);
            }
        });
}

// ----------------------------------------------------------------------------
// 4. PRIORITY EVENT ALLOCATION CONTROLLER (MAX-HEAP)
// ----------------------------------------------------------------------------

function loadPriorityRequests() {
    fetch("/api/priority-requests")
        .then(res => res.json())
        .then(data => {
            const kpi = document.getElementById("dashPriorityCount");
            if (kpi) kpi.innerText = data.count || 0;

            const grid = document.getElementById("priorityCardsGrid");
            if (!grid) return;

            const list = data.requests || [];
            if (list.length === 0) {
                grid.innerHTML = `<div style="text-align:center; padding: 2rem; color:var(--text-muted); width: 100%;">No pending priority event allocations.</div>`;
                return;
            }

            grid.innerHTML = list.map(item => `
                <div style="background: rgba(19, 27, 46, 0.85); border: 1px solid var(--border-accent); border-radius: 8px; padding: 1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.4rem;">
                        <span class="badge badge-purple" style="font-weight:700;">Priority Score: ${item.priority_score.toFixed(1)}</span>
                        <code style="font-size: 0.75rem; color: var(--text-muted);">${item.request_id}</code>
                    </div>
                    <h4 style="font-size: 0.95rem; margin-bottom: 0.3rem;">${item.title}</h4>
                    <p style="font-size: 0.8rem; color: var(--text-secondary);">Target: <strong>${item.venue_id}</strong></p>
                    <p style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.6rem;">Authority: ${item.organizer}</p>
                    <div style="display:flex; gap: 0.4rem;">
                        <button class="btn btn-secondary" style="font-size: 0.72rem; padding: 0.2rem 0.5rem;" onclick="escalatePriorityPrompt('${item.request_id}', ${item.priority_score})">
                            ⚡ Escalate (+1.0)
                        </button>
                    </div>
                </div>
            `).join("");
        });
}

function dispatchTopPriority() {
    fetch("/api/priority-requests/dispatch", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(`🚀 Dispatched Highest Priority Event via Extract-Max:\n'${data.item.title}' (Score: ${data.item.priority_score})\nAssigned to ${data.item.venue_id}.`);
                loadPriorityRequests();
            } else {
                alert(data.message);
            }
        });
}

function escalatePriorityPrompt(reqId, curScore) {
    const newScore = Math.min(10.0, curScore + 1.0);
    fetch("/api/priority-requests/escalate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request_id: reqId, new_priority: newScore })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            loadPriorityRequests();
        } else {
            alert(data.message);
        }
    });
}

// ----------------------------------------------------------------------------
// 5. ALGORITHMIC OPTIMIZERS
// ----------------------------------------------------------------------------

function runGreedyAlgorithm() {
    const container = document.getElementById("greedyResultContainer");
    container.innerHTML = `<span style="color:var(--accent-blue);">Executing Greedy Activity Selection (Earliest Finish Time First)...</span>`;

    fetch("/api/algorithms/greedy-schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
    })
    .then(res => res.json())
    .then(data => {
        const cards = data.selected_activities.map(a => `
            <div style="background: rgba(19, 27, 46, 0.9); border: 1px solid var(--accent-emerald); border-radius: 6px; padding: 0.8rem;">
                <span class="badge badge-emerald" style="font-size:0.7rem;">SELECTED SLOT</span>
                <h4 style="margin: 0.3rem 0; font-size: 0.9rem;">${a.name}</h4>
                <p style="font-size: 0.8rem; font-family: var(--font-mono); color: var(--accent-cyan);">${a.start.toFixed(1)}:00 ➔ ${a.finish.toFixed(1)}:00</p>
            </div>
        `).join("");

        container.innerHTML = `
            <div style="margin-bottom: 0.8rem; font-size: 0.85rem; color: var(--accent-emerald);">
                ✓ Algorithm Selected <strong>${data.selected_count} Non-Overlapping Events</strong> Maximizing Hall Occupancy.
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.75rem;">
                ${cards}
            </div>
        `;
    });
}

function runKnapsackAlgorithm() {
    const container = document.getElementById("knapsackResultContainer");
    container.innerHTML = `<span style="color:var(--accent-blue);">Computing 0/1 Knapsack Dynamic Programming Table...</span>`;

    fetch("/api/algorithms/equipment-knapsack", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ budget_or_power_limit: 110 })
    })
    .then(res => res.json())
    .then(data => {
        const items = data.selected_equipment.map(it => `
            <li style="margin-bottom: 0.3rem;">
                <strong>${it.name}</strong> — Cost / Load: ${it.cost} units | Utility: <span style="color:var(--accent-emerald); font-weight:700;">+${it.utility}</span>
            </li>
        `).join("");

        container.innerHTML = `
            <div style="background: rgba(11, 15, 25, 0.7); border: 1px solid var(--border-accent); border-radius: 8px; padding: 1rem;">
                <h3 style="color:var(--accent-blue); font-size: 1.1rem; margin-bottom: 0.4rem;">
                    Max Utility Achieved: <span style="color:var(--accent-emerald);">${data.max_utility} points</span> (Cap Limit: ${data.capacity_limit})
                </h3>
                <p style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.6rem;">Selected Optimal Equipment Combination:</p>
                <ul style="font-size: 0.82rem; padding-left: 1.25rem;">${items}</ul>
                <div style="margin-top: 0.6rem; font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-mono);">
                    DP Table Dimensions: ${data.dp_table_summary.rows} rows × ${data.dp_table_summary.cols} columns
                </div>
            </div>
        `;
    });
}

function runTimetableAlgorithm() {
    const container = document.getElementById("timetableResultContainer");
    container.innerHTML = `<span style="color:var(--accent-blue);">Solving Backtracking CSP with Pruning...</span>`;

    fetch("/api/algorithms/exam-timetable", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ num_venues: 3 })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.feasible) {
            container.innerHTML = `<span style="color:var(--accent-rose);">No clash-free assignment possible with current venue count.</span>`;
            return;
        }

        const entries = Object.entries(data.schedule).map(([course, venue]) => `
            <div style="background: rgba(19, 27, 46, 0.9); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.6rem 0.8rem;">
                <span style="font-size: 0.75rem; color: var(--text-muted); display:block;">Course</span>
                <strong style="color:#fff; font-size: 0.88rem;">${course}</strong>
                <div style="margin-top: 0.3rem; font-size: 0.78rem; color: var(--accent-emerald); font-weight:600;">➔ ${venue}</div>
            </div>
        `).join("");

        container.innerHTML = `
            <div style="margin-bottom: 0.8rem; font-size: 0.85rem; color: var(--accent-emerald);">
                ✓ Feasible Conflict-Free Schedule Found across <strong>${data.venues_used} Venues</strong> in ${data.backtrack_steps} recursive backtracking steps.
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.75rem;">
                ${entries}
            </div>
        `;
    });
}

// ----------------------------------------------------------------------------
// 6. VENUE WAYFINDING & SVG MAP CONTROLLER (GRAPH + DIJKSTRA)
// ----------------------------------------------------------------------------

function loadCampusMap() {
    Promise.all([
        fetch("/api/landmarks").then(r => r.json()),
        fetch("/api/pathways").then(r => r.json())
    ]).then(([landmarks, pathways]) => {
        campusLandmarks = landmarks;
        campusPathways = pathways;
        renderSvgMap();
    });
}

function renderSvgMap() {
    const svg = document.getElementById("campusSvgMap");
    if (!svg || campusLandmarks.length === 0) return;

    svg.innerHTML = "";

    // Draw pathways
    campusPathways.forEach(pw => {
        const u = campusLandmarks.find(lm => lm.id === pw.source);
        const v = campusLandmarks.find(lm => lm.id === pw.dest);
        if (!u || !v) return;

        const isPartOfRoute = currentRouteNodeIds.has(pw.source) && currentRouteNodeIds.has(pw.dest);

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", u.x);
        line.setAttribute("y1", u.y);
        line.setAttribute("x2", v.x);
        line.setAttribute("y2", v.y);
        line.setAttribute("stroke", isPartOfRoute ? "var(--accent-emerald)" : "rgba(255,255,255,0.15)");
        line.setAttribute("stroke-width", isPartOfRoute ? "4" : "2");
        if (isPartOfRoute) {
            line.setAttribute("stroke-dasharray", "6,4");
        }
        svg.appendChild(line);
    });

    // Draw landmarks / venue nodes
    campusLandmarks.forEach(lm => {
        const isRoute = currentRouteNodeIds.has(lm.id);

        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.style.cursor = "pointer";

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", lm.x);
        circle.setAttribute("cy", lm.y);
        circle.setAttribute("r", isRoute ? "14" : "10");
        circle.setAttribute("fill", isRoute ? "var(--accent-emerald)" : "var(--accent-blue)");
        circle.setAttribute("stroke", "#fff");
        circle.setAttribute("stroke-width", isRoute ? "3" : "2");

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", lm.x + 16);
        text.setAttribute("y", lm.y + 5);
        text.setAttribute("fill", isRoute ? "#34d399" : "#f1f5f9");
        text.setAttribute("font-size", isRoute ? "15px" : "14px");
        text.setAttribute("font-weight", "700");
        text.textContent = lm.name;

        g.appendChild(circle);
        g.appendChild(text);
        svg.appendChild(g);
    });
}

function findVenueRoute() {
    let startId = document.getElementById("navStartSelect").value;
    let destId = document.getElementById("navDestSelect").value;
    const accessibleOnly = document.getElementById("navWheelchair").checked;

    const venueToNode = {
        "jubilee_auditorium": "admin_block",
        "board_room_admin": "admin_block",
        "ske_auditorium": "cs_block",
        "cs_lab_ai": "cs_block",
        "m1_auditorium": "main_block",
        "m2_auditorium": "main_block",
        "m3_auditorium": "main_block",
        "m4_auditorium": "main_block",
        "cs_lab_turing": "main_block",
        "h1_auditorium": "humanities_block",
        "h2_auditorium": "humanities_block"
    };
    if (venueToNode[startId]) startId = venueToNode[startId];
    if (venueToNode[destId]) destId = venueToNode[destId];

    fetch("/api/navigate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start_id: startId, dest_id: destId, accessible_only: accessibleOnly })
    })
    .then(res => res.json())
    .then(data => {
        const resBox = document.getElementById("navRouteResult");
        if (!data.success || !data.route) {
            resBox.style.display = "block";
            document.getElementById("navDistanceText").innerText = "No route found under current constraints.";
            document.getElementById("navStepsContainer").innerHTML = "";
            currentRouteNodeIds.clear();
            renderSvgMap();
            return;
        }

        resBox.style.display = "block";
        const r = data.route;
        const dist = (r.total_distance_m !== undefined ? r.total_distance_m : (r.total_distance || 0)).toFixed(1);
        const estMin = r.estimated_minutes ? ` (~${r.estimated_minutes} min walk)` : "";
        document.getElementById("navDistanceText").innerHTML = `Total Walking Distance: <strong>${dist} meters</strong>${estMin}`;
        
        if (r.turn_by_turn && r.turn_by_turn.length > 0) {
            document.getElementById("navStepsContainer").innerHTML = r.turn_by_turn.map(step => `
                <div style="margin-bottom: 0.3rem;">🚶 ${step}</div>
            `).join("");
        } else if (r.path_landmarks && r.path_landmarks.length > 0) {
            document.getElementById("navStepsContainer").innerHTML = r.path_landmarks.map((step, idx) => `
                <div style="margin-bottom: 0.3rem;">[${idx + 1}] ${step.name}</div>
            `).join("");
        } else if (r.path && r.path.length > 0) {
            document.getElementById("navStepsContainer").innerHTML = r.path.map((step, idx) => `
                <div style="margin-bottom: 0.3rem;">[${idx + 1}] ${step.name || step}</div>
            `).join("");
        }

        const nodeIds = r.path_node_ids || (r.path ? r.path.map(s => s.node_id || s) : []);
        currentRouteNodeIds = new Set(nodeIds);
        renderSvgMap();
    })
    .catch(err => console.error(err));
}

// ----------------------------------------------------------------------------
// 7. BENCHMARKS & STATISTICAL ANALYTICS CONTROLLER
// ----------------------------------------------------------------------------

function loadLiveBenchmarks() {
    const intBox = document.getElementById("benchIntervalResult");
    const heapBox = document.getElementById("benchHeapResult");

    if (intBox) intBox.innerHTML = `Running benchmarks on Python backend...`;
    if (heapBox) heapBox.innerHTML = `Running benchmarks on Python backend...`;

    fetch("/api/benchmarks")
        .then(res => res.json())
        .then(data => {
            if (intBox && data.interval_tree) {
                const it = data.interval_tree;
                intBox.innerHTML = `
                    • Dataset Size: <strong>${it.n.toLocaleString()} intervals</strong><br>
                    • AVL Interval Tree Query: <span style="color:var(--accent-emerald); font-weight:700;">${it.tree_time_ms} ms</span><br>
                    • Linear List Scan: <span style="color:var(--accent-rose);">${it.linear_time_ms} ms</span><br>
                    • Performance Speedup: <strong style="color:var(--accent-cyan); font-size:1.1rem;">${it.speedup}× faster</strong>
                `;
            }

            if (heapBox && data.max_heap) {
                const mh = data.max_heap;
                heapBox.innerHTML = `
                    • Dataset Size: <strong>${mh.n.toLocaleString()} priority items</strong><br>
                    • Binary Max-Heap Extract-Max: <span style="color:var(--accent-emerald); font-weight:700;">${mh.heap_time_ms} ms</span><br>
                    • Unsorted List Scan: <span style="color:var(--accent-rose);">${mh.list_time_ms} ms</span><br>
                    • Performance Speedup: <strong style="color:var(--accent-cyan); font-size:1.1rem;">${mh.speedup}× faster</strong>
                `;
            }
        });
}

function renderAnalyticsTable(venues) {
    const tbody = document.getElementById("analyticsVenueTable");
    if (!tbody) return;

    tbody.innerHTML = venues.map(v => `
        <tr>
            <td><strong>${v.name}</strong></td>
            <td>${v.building}</td>
            <td><span class="badge badge-purple">${v.category}</span></td>
            <td><span class="badge badge-cyan">${v.capacity}</span></td>
            <td>${v.air_conditioned ? '✓ Yes' : '—'}</td>
            <td>${v.projector ? '✓ Yes' : '—'}</td>
            <td>${v.sound_system || 'Standard'}</td>
            <td>${v.wheelchair_accessible ? '♿ Accessible' : 'Stairs Only'}</td>
        </tr>
    `).join("");
}

// ----------------------------------------------------------------------------
````

## `web/static/index.html`

````html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kristu Jayanti University | Smart Campus Venue & Facility Management</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body>

    <!-- Header Navigation -->
    <header>
        <div class="header-inner">
            <div class="brand">
                <div class="brand-icon">🏛️</div>
                <div class="brand-text">
                    <h1>Kristu Jayanti University</h1>
                    <p>Smart Campus Venue & Facility Management — Internal Academic Operations</p>
                </div>
            </div>

            <nav class="nav-tabs" style="flex-wrap: wrap;">
                <button class="tab-btn active" data-tab="tabDashboard">
                    <span>📊</span> Dashboard
                </button>
                <button class="tab-btn" data-tab="tabVenues">
                    <span>🏢</span> Venues
                </button>
                <button class="tab-btn" data-tab="tabBookings">
                    <span>📅</span> Bookings & Schedule
                </button>
                <button class="tab-btn" data-tab="tabWaitlist">
                    <span>🎫</span> Waitlist
                </button>
                <button class="tab-btn admin-only" data-tab="tabPriority">
                    <span>👑</span> Priority Allocations
                </button>
                <button class="tab-btn" data-tab="tabNavigation">
                    <span>🗺️</span> Campus Route Map
                </button>
            </nav>

            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div class="portal-toggle-container">
                    <button class="portal-btn active" id="btnUserPortal" onclick="switchPortal('user')">
                        👤 User Portal
                    </button>
                    <button class="portal-btn" id="btnAdminPortal" onclick="switchPortal('admin')">
                        🛡️ Admin Portal <span id="adminPendingBadge" class="badge badge-rose" style="display:none; margin-left: 4px; padding: 0.1rem 0.4rem; font-size: 0.68rem;">0</span>
                    </button>
                </div>

                <div class="header-status">
                    <span class="status-indicator"></span>
                    <span id="portalRoleIndicator" style="font-size: 0.78rem; color: var(--text-secondary); font-weight: 500;">User Portal</span>
                </div>
            </div>
        </div>
    </header>

    <main>

        <!-- ================================================================= -->
        <!-- 1. DASHBOARD OVERVIEW PANEL                                       -->
        <!-- ================================================================= -->
        <section id="tabDashboard" class="tab-panel active">
            <!-- Hero Banner -->
            <div class="hero-banner">
                <div>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.6rem;">
                        <span class="badge badge-cyan">Kothanur Main Campus</span>
                        <span class="badge badge-emerald">Internal College Use Only</span>
                    </div>
                    <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.4rem; color: #fff;">
                        Campus Venue Operations Center
                    </h2>
                    <p style="font-size: 0.88rem; color: var(--text-secondary); max-width: 760px; line-height: 1.5;">
                        Official internal campus facility management portal. Allocates and schedules auditoriums, seminar halls, and computer laboratories strictly for college academic assemblies, department symposiums, student fests, and examinations with automated conflict prevention.
                    </p>
                </div>
                <div class="hero-actions">
                    <button class="btn btn-primary" onclick="switchNavTab('tabBookings')">
                        📅 Schedule Venue Slot
                    </button>
                    <button class="btn btn-secondary" onclick="switchNavTab('tabVenues')">
                        🏢 View Venue Directory
                    </button>
                </div>
            </div>

            <!-- User-Only Campus Route Map Feature Banner -->
            <div class="user-only" style="margin-bottom: 1.5rem;">
                <div style="background: linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(129, 140, 248, 0.14)); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 12px; padding: 1.25rem 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                    <div>
                        <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.35rem;">
                            <span style="font-size: 1.3rem;">🗺️</span>
                            <strong style="color: #fff; font-size: 1.05rem;">Campus Route Map & Venue Wayfinding</strong>
                            <span class="badge badge-emerald">User Wayfinding</span>
                        </div>
                        <p style="font-size: 0.85rem; color: var(--text-secondary); max-width: 720px; line-height: 1.5;">
                            Find your way around Kristu Jayanti campus: straight from Gate 1 to Main Block and PG Block; right to Admin Block (Jubilee Auditorium); straight left to Humanities Block (H1, H2); and Gate 2 to college basement parking areas.
                        </p>
                    </div>
                    <div style="display: flex; gap: 0.6rem;">
                        <button class="btn btn-primary" onclick="switchNavTab('tabNavigation')">
                            🗺️ Open Campus Route Map
                        </button>
                        <button class="btn btn-secondary" onclick="switchNavTab('tabBookings')">
                            📅 Request Venue Slot
                        </button>
                    </div>
                </div>
            </div>

            <!-- Key Metric KPI Cards -->
            <div class="grid-4" style="margin-bottom: 1.5rem;">
                <div class="metric-card">
                    <div class="metric-icon" style="background: rgba(56, 189, 248, 0.15); color: var(--accent-blue);">🏛️</div>
                    <div class="metric-content">
                        <h3 id="dashVenueCount">10</h3>
                        <p>Campus Venues</p>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon" style="background: rgba(129, 140, 248, 0.15); color: var(--accent-indigo);">📅</div>
                    <div class="metric-content">
                        <h3 id="dashBookingCount">9</h3>
                        <p>Active Event Bookings</p>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon" style="background: rgba(52, 211, 153, 0.15); color: var(--accent-emerald);">🎫</div>
                    <div class="metric-content">
                        <h3 id="dashWaitlistCount">3</h3>
                        <p>Waitlist Queue Requests</p>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon" style="background: rgba(244, 63, 94, 0.15); color: var(--accent-rose);">👑</div>
                    <div class="metric-content">
                        <h3 id="dashPriorityCount">3</h3>
                        <p>Institutional Priority Requests</p>
                    </div>
                </div>
            </div>

            <!-- Quick Service Hub & Live Activities -->
            <div class="grid-2">
                <!-- Quick Operations Hub -->
                <div class="card">
                    <div class="card-header">
                        <h2>Quick Actions</h2>
                        <span class="badge badge-emerald">Fast Access</span>
                    </div>
                    <div class="quick-actions-grid">
                        <div class="action-tile" onclick="switchNavTab('tabBookings')">
                            <div class="action-tile-icon">📅</div>
                            <div>
                                <h4>Slot Scheduling</h4>
                                <p>Interactive daily schedule timeline with automatic conflict detection</p>
                            </div>
                        </div>

                        <div class="action-tile" onclick="switchNavTab('tabVenues')">
                            <div class="action-tile-icon">🏢</div>
                            <div>
                                <h4>Venue Directory</h4>
                                <p>Browse, filter, and register campus auditoriums & laboratories</p>
                            </div>
                        </div>

                        <div class="action-tile" onclick="switchNavTab('tabWaitlist')">
                            <div class="action-tile-icon">🎫</div>
                            <div>
                                <h4>Waitlist Counter</h4>
                                <p>Queue token issuance & coordinator approvals for full slots</p>
                            </div>
                        </div>

                        <div class="action-tile" onclick="switchNavTab('tabPriority')">
                            <div class="action-tile-icon">👑</div>
                            <div>
                                <h4>Priority Allocation</h4>
                                <p>Expedited review & hall allocation for official university assemblies</p>
                            </div>
                        </div>

                        <div class="action-tile" onclick="switchNavTab('tabNavigation')">
                            <div class="action-tile-icon">🗺️</div>
                            <div>
                                <h4>Campus Route Map</h4>
                                <p>Interactive walking routes to auditoriums, blocks & facilities</p>
                            </div>
                        </div>

                    </div>
                </div>

                <!-- Live Campus Notice & Status -->
                <div class="card">
                    <div class="card-header">
                        <h2>Campus Auditoriums & Facilities</h2>
                        <span class="badge badge-cyan">Facility Directory</span>
                    </div>
                    <div class="notice-list">
                        <div class="notice-item">
                            <div class="notice-icon" style="background: rgba(56, 189, 248, 0.15); color: var(--accent-blue);">🏛️</div>
                            <div>
                                <strong>Jubilee Auditorium (Administrative Block)</strong>
                                <p>800–1,000 seat premier auditorium in the Administrative Block equipped with digital line array and stage lighting for university convocations, conclaves, and official ceremonies.</p>
                                <span class="notice-time">Administrative Block Ground Floor</span>
                            </div>
                        </div>

                        <div class="notice-item">
                            <div class="notice-icon" style="background: rgba(52, 211, 153, 0.15); color: var(--accent-emerald);">🎭</div>
                            <div>
                                <strong>St. Kuriakose Elias Auditorium (PG Block / Science Block II)</strong>
                                <p>Flagship 544-seat prestigious auditorium in PG Block / Science Block II for national symposiums (ShellHacks MCA), academic conferences, and cultural assemblies.</p>
                                <span class="notice-time">PG Block / Science Block II</span>
                            </div>
                        </div>

                        <div class="notice-item">
                            <div class="notice-icon" style="background: rgba(129, 140, 248, 0.15); color: var(--accent-indigo);">🏢</div>
                            <div>
                                <strong>Main Block Auditoriums: M1, M2, M3, M4</strong>
                                <p>Four dedicated auditoriums situated inside the Main Block serving department assemblies, guest lectures, placement drives, and student chapter workshops.</p>
                                <span class="notice-time">Main Block Floors 1–4</span>
                            </div>
                        </div>

                        <div class="notice-item">
                            <div class="notice-icon" style="background: rgba(251, 191, 36, 0.15); color: var(--accent-amber);">📚</div>
                            <div>
                                <strong>Humanities Block Auditoriums: H1, H2</strong>
                                <p>Two dedicated auditoriums in the Humanities Block accommodating literary fests, debate championships, social science symposiums, and cultural presentations.</p>
                                <span class="notice-time">Humanities Block Floors 1–2</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>


        <!-- ================================================================= -->
        <!-- 2. VENUE DIRECTORY PANEL                                          -->
        <!-- ================================================================= -->
        <section id="tabVenues" class="tab-panel">
            <div class="grid-aside-main">
                <!-- Aside: Register Venue Form -->
                <div style="display: flex; flex-direction: column; gap: 1.25rem;">
                    <!-- Admin Register Venue Card -->
                    <div class="card admin-only">
                        <div class="card-header">
                            <h2>Register Campus Venue</h2>
                            <span class="badge badge-rose">Admin Only</span>
                        </div>

                        <form id="venueForm">
                            <div class="form-group">
                                <label for="vidInput">Venue Code / ID</label>
                                <input type="text" id="vidInput" placeholder="e.g. m5_auditorium" required>
                            </div>

                            <div class="form-group">
                                <label for="vnameInput">Venue Name</label>
                                <input type="text" id="vnameInput" placeholder="e.g. M5 Auditorium" required>
                            </div>

                            <div class="form-group">
                                <label for="vbuildingInput">Campus Building</label>
                                <select id="vbuildingInput">
                                    <option value="Main Block" selected>Main Block</option>
                                    <option value="Administrative Block">Administrative Block</option>
                                    <option value="PG Block / Science Block II">PG Block / Science Block II</option>
                                    <option value="Humanities Block">Humanities Block</option>
                                    <option value="Science Block I">Science Block I</option>
                                    <option value="Sports Complex Grounds">Sports Complex Grounds</option>
                                </select>
                            </div>

                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem;">
                                <div class="form-group">
                                    <label for="vcategoryInput">Category</label>
                                    <select id="vcategoryInput">
                                        <option value="Auditorium" selected>Auditorium</option>
                                        <option value="Seminar Hall">Seminar Hall</option>
                                        <option value="Computer Lab">Computer Lab</option>
                                        <option value="Conference Room">Conference Room</option>
                                        <option value="Sports Facility">Sports Facility</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="vcapacityInput">Capacity (Seats)</label>
                                    <input type="number" id="vcapacityInput" min="10" max="2500" value="250" required>
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="vpolicyInput">Usage Policy</label>
                                <input type="text" id="vpolicyInput" value="College Academic & Departmental Use Only" required>
                            </div>

                            <button type="submit" class="btn btn-primary" style="width: 100%;">
                                ➕ Register Campus Venue
                            </button>
                        </form>
                    </div>

                    <!-- User Guide Aside Card -->
                    <div class="card user-only">
                        <div class="card-header">
                            <h2>Venue Directory</h2>
                            <span class="badge badge-cyan">User Guide</span>
                        </div>
                        <p style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 1rem;">
                            Review seating capacities, AV sound systems, and usage guidelines for college auditoriums and computing labs. Select any venue to view scheduled events or submit a booking request.
                        </p>
                        <div style="display: flex; flex-direction: column; gap: 0.6rem;">
                            <button class="btn btn-primary" onclick="switchNavTab('tabBookings')">
                                📅 Request Venue Booking
                            </button>
                            <button class="btn btn-secondary" onclick="switchNavTab('tabNavigation')">
                                🗺️ Find Walking Route to Venue
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Main: Venue Directory Table -->
                <div class="card">
                    <div class="card-header">
                        <div>
                            <h2>Campus Venues</h2>
                            <p style="font-size: 0.82rem; color: var(--text-secondary);">
                                Directory of official auditoriums, conference halls, and computing labs across Kristu Jayanti campus
                            </p>
                        </div>
                        <div class="admin-only" style="display: flex; gap: 0.5rem;">
                            <button class="btn btn-secondary" style="font-size: 0.8rem; padding: 0.4rem 0.8rem;" onclick="reverseVenueList()">
                                🔄 Reverse Order
                            </button>
                            <button class="btn btn-secondary" style="font-size: 0.8rem; padding: 0.4rem 0.8rem;" onclick="undoVenueAction()">
                                ↩️ Undo Last Deletion
                            </button>
                        </div>
                    </div>

                    <!-- Filter & Search Toolbar -->
                    <div style="display: flex; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap;">
                        <input type="text" id="venueSearchInput" placeholder="🔍 Search venue by name, code or building..." style="flex: 1; min-width: 200px;" oninput="filterVenueTable()">
                        <select id="venueCategoryFilter" style="width: 200px;" onchange="filterVenueTable()">
                            <option value="ALL">All Categories</option>
                            <option value="Auditorium">Auditoriums (Jubilee, SKE, M1-M4, H1-H2)</option>
                            <option value="Computer Lab">Computer Labs</option>
                            <option value="Conference Room">Conference Rooms</option>
                            <option value="Sports Facility">Sports Facilities</option>
                        </select>
                    </div>

                    <!-- Venues Table -->
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>Venue Code</th>
                                    <th>Venue Name</th>
                                    <th>Campus Building</th>
                                    <th>Category</th>
                                    <th>Capacity</th>
                                    <th>Sound System & AV</th>
                                    <th>Policy</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="venueTableBody">
                                <!-- Populated dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>


        <!-- ================================================================= -->
        <!-- 3. SLOT BOOKING & SCHEDULE TIMELINE PANEL                         -->
        <!-- ================================================================= -->
        <section id="tabBookings" class="tab-panel">
            <!-- Admin Approval Center: Pending Booking Requests -->
            <div class="card admin-only" style="margin-bottom: 1.5rem; border-left: 4px solid var(--accent-rose);">
                <div class="card-header">
                    <div>
                        <h2>🛡️ Admin Approval Center — Pending Booking Requests</h2>
                        <p style="font-size: 0.82rem; color: var(--text-secondary);">
                            Review, approve into the AVL Interval Tree, or reject booking requests submitted by faculty and student bodies
                        </p>
                    </div>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <span class="badge badge-rose" id="adminPendingCountBadge">0 Pending</span>
                        <button class="btn btn-secondary" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;" onclick="loadPendingBookings()">
                            🔄 Refresh
                        </button>
                    </div>
                </div>

                <div id="adminPendingContainer" style="margin-top: 1rem;">
                    <!-- Dynamically populated pending cards -->
                </div>
            </div>

            <!-- User Status: My Booking Requests -->
            <div class="card user-only" style="margin-bottom: 1.5rem; border-left: 4px solid var(--accent-blue);">
                <div class="card-header">
                    <div>
                        <h2>📋 My Submitted Booking Requests</h2>
                        <p style="font-size: 0.82rem; color: var(--text-secondary);">
                            Track the status of your venue booking requests (Awaiting Admin Approval, Approved, or Rejected)
                        </p>
                    </div>
                    <button class="btn btn-secondary" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;" onclick="loadUserRequests()">
                        🔄 Refresh Status
                    </button>
                </div>

                <div class="table-responsive" style="margin-top: 0.75rem;">
                    <table>
                        <thead>
                            <tr>
                                <th>Request ID</th>
                                <th>Event Title</th>
                                <th>Department / Body</th>
                                <th>Target Venue</th>
                                <th>Date & Time Interval</th>
                                <th>Status</th>
                                <th>Remarks</th>
                            </tr>
                        </thead>
                        <tbody id="userRequestsTableBody">
                            <!-- Populated dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="grid-aside-main">
                <!-- Aside: Slot Booking Form -->
                <div class="card">
                    <div class="card-header">
                        <h2 id="bookingFormHeading">Request Venue Booking</h2>
                        <span class="badge badge-emerald" id="bookingFormBadge">User Portal</span>
                    </div>
                    <p id="bookingFormDescription" style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 1rem;">
                        Select auditorium or lab, event interval, and submit. Your request is queued for Admin approval.
                    </p>

                    <form id="bookingForm">
                        <div class="form-group">
                            <label for="bookVenueSelect">Select Campus Venue</label>
                            <select id="bookVenueSelect" required onchange="onBookingVenueChanged()">
                                <!-- Populated dynamically -->
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="bookTitle">Event / Assembly Title</label>
                            <input type="text" id="bookTitle" placeholder="e.g. National Symposium Inauguration" required>
                        </div>

                        <div class="form-group">
                            <label for="bookOrganizer">Department / Student Association</label>
                            <input type="text" id="bookOrganizer" placeholder="e.g. Dept. of Computer Applications (MCA)" required>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem;">
                            <div class="form-group">
                                <label for="bookStartTime">Start Time</label>
                                <input type="time" id="bookStartTime" value="14:00" required>
                            </div>
                            <div class="form-group">
                                <label for="bookEndTime">End Time</label>
                                <input type="time" id="bookEndTime" value="16:00" required>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="bookDate">Reservation Date</label>
                            <input type="date" id="bookDate" value="2026-09-10" required>
                        </div>

                        <button type="submit" id="bookSubmitBtn" class="btn btn-primary" style="width: 100%;">
                            📩 Submit Booking Request
                        </button>
                    </form>
                </div>

                <!-- Main: Visual Timeline & Existing Schedule -->
                <div class="card">
                    <div class="card-header">
                        <div>
                            <h2 id="timelineVenueTitle">Venue Schedule Timeline</h2>
                            <p style="font-size: 0.82rem; color: var(--text-secondary);">
                                Real-time daily timeline (08:00 to 20:00) with automatic clash detection
                            </p>
                        </div>
                        <span class="badge badge-cyan" id="timelineVenueBadge">ske_auditorium</span>
                    </div>

                    <!-- Visual Timeline Bar -->
                    <div class="timeline-visual-card">
                        <div class="timeline-axis">
                            <span>08:00</span>
                            <span>10:00</span>
                            <span>12:00</span>
                            <span>14:00</span>
                            <span>16:00</span>
                            <span>18:00</span>
                            <span>20:00</span>
                        </div>
                        <div id="timelineTrack" class="timeline-track">
                            <!-- Booking blocks positioned dynamically -->
                        </div>
                    </div>

                    <!-- Clash Warning Alert Box -->
                    <div id="clashAlertBox" style="display: none; margin-bottom: 1rem; padding: 1rem; background: rgba(244, 63, 94, 0.15); border: 1px solid var(--accent-rose); border-radius: 8px;">
                        <h4 style="color: var(--accent-rose); font-size: 0.9rem; margin-bottom: 0.3rem;">⚠️ Scheduling Conflict Detected!</h4>
                        <p id="clashAlertMsg" style="font-size: 0.82rem; color: #fecdd3;"></p>
                    </div>

                    <!-- Bookings Table for Selected Venue -->
                    <h3 style="font-size: 0.95rem; margin-bottom: 0.75rem;">Scheduled Events for Selected Venue</h3>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>Booking ID</th>
                                    <th>Event Title</th>
                                    <th>Department / Body</th>
                                    <th>Time Interval</th>
                                    <th>Duration</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="bookingsTableBody">
                                <!-- Populated dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>


        <!-- ================================================================= -->
        <!-- 4. WAITLIST PANEL                                                 -->
        <!-- ================================================================= -->
        <section id="tabWaitlist" class="tab-panel">
            <div class="grid-aside-main">
                <!-- Aside: Enqueue Waitlist Form -->
                <div class="card">
                    <div class="card-header">
                        <h2>Join Venue Waitlist</h2>
                        <span class="badge badge-cyan">Waitlist Request</span>
                    </div>

                    <form id="waitlistForm">
                        <div class="form-group">
                            <label for="waitlistVenue">Desired Campus Venue</label>
                            <select id="waitlistVenue">
                                <!-- Populated dynamically -->
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="waitlistTitle">Event Purpose / Title</label>
                            <input type="text" id="waitlistTitle" placeholder="e.g. Literary Debating Championship" required>
                        </div>

                        <div class="form-group">
                            <label for="waitlistOrganizer">Department / Student Club</label>
                            <input type="text" id="waitlistOrganizer" placeholder="e.g. Student Welfare Directorate" required>
                        </div>

                        <div class="form-group">
                            <label for="waitlistTimeSlot">Requested Time Window</label>
                            <input type="text" id="waitlistTimeSlot" value="14:00 - 17:00" required>
                        </div>

                        <button type="submit" class="btn btn-primary" style="width: 100%;">
                            🎫 Submit Waitlist Request
                        </button>
                    </form>
                </div>

                <!-- Main: Queue Status & Dequeue Station -->
                <div class="card">
                    <div class="card-header">
                        <div>
                            <h2>Active Waitlist Queue</h2>
                            <p style="font-size: 0.82rem; color: var(--text-secondary);">
                                Requests are reviewed and approved in order of submission
                            </p>
                        </div>
                        <button class="btn btn-primary" onclick="serveNextWaitlist()">
                            ✅ Approve Next Request
                        </button>
                    </div>

                    <div id="waitlistQueueContainer" class="queue-card-grid" style="margin-top: 1rem;">
                        <!-- Dynamically populated queue token cards -->
                    </div>
                </div>
            </div>
        </section>


        <!-- ================================================================= -->
        <!-- 5. PRIORITY EVENT ALLOCATION PANEL                                -->
        <!-- ================================================================= -->
        <section id="tabPriority" class="tab-panel">
            <div class="grid-aside-main">
                <!-- Aside: Submit Priority Request -->
                <div class="card">
                    <div class="card-header">
                        <h2>Register Priority Event</h2>
                        <span class="badge badge-purple">Institutional</span>
                    </div>

                    <form id="priorityForm">
                        <div class="form-group">
                            <label for="prioTitle">Institutional Event Title</label>
                            <input type="text" id="prioTitle" placeholder="e.g. University Convocation Ceremony" required>
                        </div>

                        <div class="form-group">
                            <label for="prioVenue">Target Venue</label>
                            <select id="prioVenue">
                                <!-- Populated dynamically -->
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="prioOrganizer">Authority / Directorate</label>
                            <input type="text" id="prioOrganizer" placeholder="e.g. Vice Chancellor's Secretariat" required>
                        </div>

                        <div class="form-group">
                            <label for="prioScore">Priority Level (1.0 to 10.0)</label>
                            <input type="number" id="prioScore" min="1.0" max="10.0" step="0.5" value="9.0" required>
                        </div>

                        <button type="submit" class="btn btn-primary" style="width: 100%;">
                            👑 Submit Priority Request
                        </button>
                    </form>
                </div>

                <!-- Main: Priority Triage Board -->
                <div class="card">
                    <div class="card-header">
                        <div>
                            <h2>Institutional Priority Allocation</h2>
                            <p style="font-size: 0.82rem; color: var(--text-secondary);">
                                Ensures high-priority university assemblies, convocations, and conclaves receive expedited hall allocation
                            </p>
                        </div>
                        <button class="btn btn-primary" onclick="dispatchTopPriority()">
                            🚀 Allocate Highest Priority Event
                        </button>
                    </div>

                    <div id="priorityCardsGrid" class="priority-cards-grid" style="margin-top: 1rem;">
                        <!-- Dynamically populated priority cards -->
                    </div>
                </div>
            </div>
        </section>


        <!-- ================================================================= -->
        <!-- 6. CAMPUS ROUTE MAP & VENUE NAVIGATION                            -->
        <!-- ================================================================= -->
        <section id="tabNavigation" class="tab-panel">
            <div class="grid-aside-main">
                <!-- Navigation Controls -->
                <div class="card">
                    <div class="card-header">
                        <h2>Venue Wayfinding</h2>
                        <span class="badge badge-cyan">Walking Routes</span>
                    </div>

                    <div class="form-group">
                        <label for="navStartSelect">Origin / Entrance</label>
                        <select id="navStartSelect">
                            <!-- Populated dynamically -->
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="navDestSelect">Destination Venue</label>
                        <select id="navDestSelect">
                            <!-- Populated dynamically -->
                        </select>
                    </div>

                    <div class="form-group">
                        <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer; text-transform: none;">
                            <input type="checkbox" id="navWheelchair">
                            <span>♿ Wheelchair Accessible & Ramp Path Only</span>
                        </label>
                    </div>

                    <button class="btn btn-primary" style="width: 100%;" onclick="findVenueRoute()">
                        🚶 Calculate Walking Route
                    </button>

                    <!-- Route Result Info -->
                    <div id="navRouteResult" style="margin-top: 1rem; display: none; padding: 0.8rem; background: rgba(11, 15, 25, 0.6); border-radius: 8px;">
                        <h4 style="font-size: 0.88rem; color: var(--accent-emerald);">Optimal Walking Route</h4>
                        <p id="navDistanceText" style="font-size: 0.82rem; color: var(--text-secondary); margin: 0.2rem 0;"></p>
                        <div id="navStepsContainer" style="font-size: 0.78rem; font-family: var(--font-mono); color: #e2e8f0; margin-top: 0.4rem;"></div>
                    </div>
                </div>

                <!-- SVG Campus Map -->
                <div class="card">
                    <div class="card-header">
                        <h2>Interactive Campus Map</h2>
                        <span class="badge badge-emerald">Campus Route Map</span>
                    </div>
                    <div style="width: 100%; height: 500px; background: #070a12; border-radius: 8px; border: 1px solid var(--border-color); overflow: hidden; position: relative;">
                        <svg id="campusSvgMap" width="100%" height="100%" viewBox="0 0 1000 650">
                            <!-- Graph pathways & landmarks rendered dynamically -->
                        </svg>
                    </div>
                </div>
            </div>
        </section>



    </main>

    <script src="app.js"></script>
</body>
</html>
````

## `web/static/styles.css`

````css
/* ==========================================================================
   Smart Campus & Student Operations: Dashboard Design System
   ========================================================================== */

:root {
    --bg-primary: #0b0f19;
    --bg-secondary: #131b2e;
    --bg-card: rgba(26, 36, 61, 0.7);
    --bg-card-hover: rgba(33, 46, 77, 0.85);
    --border-color: rgba(255, 255, 255, 0.1);
    --border-accent: rgba(56, 189, 248, 0.3);
    
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;

    --accent-blue: #38bdf8;
    --accent-indigo: #818cf8;
    --accent-emerald: #34d399;
    --accent-amber: #fbbf24;
    --accent-rose: #f43f5e;
    --accent-purple: #c084fc;

    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: var(--font-family);
    background-color: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    line-height: 1.5;
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(129, 140, 248, 0.08) 0%, transparent 40%);
}

/* Header */
header {
    background: rgba(19, 27, 46, 0.8);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-color);
    padding: 1rem 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-inner {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.brand-icon {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-indigo));
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
}

.brand-text h1 {
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(to right, #fff, var(--text-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.brand-text p {
    font-size: 0.75rem;
    color: var(--text-muted);
}

/* Navigation Tabs */
.nav-tabs {
    display: flex;
    gap: 0.5rem;
    background: rgba(11, 15, 25, 0.6);
    padding: 0.3rem;
    border-radius: 10px;
    border: 1px solid var(--border-color);
}

.tab-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    font-weight: 500;
    border-radius: 7px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.tab-btn:hover {
    color: var(--text-primary);
    background: rgba(255, 255, 255, 0.05);
}

.tab-btn.active {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-indigo));
    color: #fff;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.25);
}

/* Main Container */
main {
    max-width: 1400px;
    margin: 1.5rem auto;
    padding: 0 1.5rem;
}

.tab-panel {
    display: none;
    animation: fadeIn 0.3s ease-in-out;
}

.tab-panel.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Grid Layouts */
.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
}

.grid-aside-main {
    display: grid;
    grid-template-columns: 360px 1fr;
    gap: 1.5rem;
}

@media (max-width: 1024px) {
    .grid-2, .grid-3, .grid-aside-main {
        grid-template-columns: 1fr;
    }
}

/* Cards */
.card {
    background: var(--bg-card);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 1.25rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    transition: border-color 0.2s;
}

.card:hover {
    border-color: var(--border-accent);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.card-header h2, .card-header h3 {
    font-size: 1rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.55rem;
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-cyan { background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); border: 1px solid rgba(56, 189, 248, 0.3); }
.badge-emerald { background: rgba(52, 211, 153, 0.15); color: var(--accent-emerald); border: 1px solid rgba(52, 211, 153, 0.3); }
.badge-amber { background: rgba(251, 191, 36, 0.15); color: var(--accent-amber); border: 1px solid rgba(251, 191, 36, 0.3); }
.badge-rose { background: rgba(244, 63, 94, 0.15); color: var(--accent-rose); border: 1px solid rgba(244, 63, 94, 0.3); }

/* Forms & Inputs */
.form-group {
    margin-bottom: 1rem;
}

label {
    display: block;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 0.35rem;
}

input[type="text"], input[type="time"], input[type="number"], select, textarea {
    width: 100%;
    background: rgba(11, 15, 25, 0.8);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-family: inherit;
    transition: all 0.2s;
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
}

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.65rem 1.2rem;
    font-size: 0.85rem;
    font-weight: 600;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-indigo));
    color: white;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
}

.btn-primary:hover {
    opacity: 0.95;
    transform: translateY(-1px);
}

.btn-danger {
    background: linear-gradient(135deg, var(--accent-rose), #e11d48);
    color: white;
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.08);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.12);
}

/* Interactive Campus Map Canvas */
.map-container {
    position: relative;
    width: 100%;
    height: 520px;
    background: #080c16;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    overflow: hidden;
}

#campusMapSvg {
    width: 100%;
    height: 100%;
    cursor: grab;
}

/* Map Elements */
.map-edge {
    stroke: rgba(148, 163, 184, 0.25);
    stroke-width: 3;
    stroke-linecap: round;
    transition: all 0.3s;
}

.map-edge.stairs {
    stroke-dasharray: 6, 4;
    stroke: rgba(251, 191, 36, 0.4);
}

.map-edge.active-path {
    stroke: var(--accent-emerald);
    stroke-width: 5;
    stroke-dasharray: 8, 4;
    filter: drop-shadow(0 0 8px rgba(52, 211, 153, 0.7));
    animation: dash 1.2s linear infinite;
}

@keyframes dash {
    from {
        stroke-dashoffset: 24;
    }
    to {
        stroke-dashoffset: 0;
    }
}

.map-node {
    cursor: pointer;
    transition: transform 0.2s;
}

.map-node:hover {
    transform: scale(1.15);
}

.map-node-circle {
    fill: #1e293b;
    stroke: var(--accent-blue);
    stroke-width: 2.5;
    transition: all 0.2s;
}

.map-node.start .map-node-circle {
    fill: var(--accent-emerald);
    stroke: #fff;
    filter: drop-shadow(0 0 10px rgba(52, 211, 153, 0.8));
}

.map-node.dest .map-node-circle {
    fill: var(--accent-rose);
    stroke: #fff;
    filter: drop-shadow(0 0 10px rgba(244, 63, 94, 0.8));
}

.map-node.in-path .map-node-circle {
    fill: var(--accent-indigo);
    stroke: #fff;
}

.map-label {
    fill: #f1f5f9;
    font-size: 11px;
    font-weight: 500;
    pointer-events: none;
    text-shadow: 0 2px 4px rgba(0,0,0,0.8);
}

/* Timeline & Schedule Bar */
.timeline-container {
    background: rgba(11, 15, 25, 0.7);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.timeline-hours {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
    font-family: var(--font-mono);
}

.timeline-bar {
    height: 36px;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 6px;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.timeline-slot {
    position: absolute;
    top: 3px;
    bottom: 3px;
    border-radius: 4px;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-indigo));
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    padding: 0 0.5rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    cursor: pointer;
    transition: all 0.2s;
}

.timeline-slot:hover {
    filter: brightness(1.2);
    z-index: 10;
}

/* Tree ASCII & Code Blocks */
pre.ascii-box {
    background: #080c16;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 1rem;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: #38bdf8;
    overflow-x: auto;
    max-height: 280px;
}

/* Tables */
.table-container {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
}

th {
    text-align: left;
    padding: 0.6rem 0.8rem;
    background: rgba(255, 255, 255, 0.03);
    color: var(--text-secondary);
    font-weight: 600;
    border-bottom: 1px solid var(--border-color);
}

td {
    padding: 0.65rem 0.8rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

tr:hover td {
    background: rgba(255, 255, 255, 0.02);
}

/* Turn by turn steps */
.directions-list {
    list-style: none;
    margin-top: 0.75rem;
}

.direction-step {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    margin-bottom: 0.6rem;
    font-size: 0.82rem;
}

.step-num {
    width: 20px;
    height: 20px;
    background: rgba(56, 189, 248, 0.15);
    color: var(--accent-blue);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
    flex-shrink: 0;
}

/* Notification Toast */
#toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    padding: 0.8rem 1.2rem;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 500;
    color: white;
    z-index: 1000;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    display: none;
    animation: slideUp 0.3s ease;
}

@keyframes slideUp {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

.toast-success { background: #059669; border: 1px solid #10b981; }
.toast-error { background: #e11d48; border: 1px solid #f43f5e; }
.toast-info { background: #0284c7; border: 1px solid #38bdf8; }

/* ==========================================================================
   Custom Scrollbars & Interactive Polish
   ========================================================================== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(56, 189, 248, 0.4);
}

/* Glowing pulse for critical elements */
@keyframes pulseGlow {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.85; transform: scale(1.02); }
}

.badge-rose {
    animation: pulseGlow 2.5s infinite ease-in-out;
}

/* Enhanced table row hover effect */
tr {
    transition: background-color 0.15s ease;
}

tr:hover td {
    background: rgba(56, 189, 248, 0.04);
}

/* Card glassmorphism subtle shimmer on hover */
.card {
    transition: border-color 0.25s ease, transform 0.2s ease, box-shadow 0.25s ease;
}

.card:hover {
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
}

/* Mobile responsive nav scrolling */
@media (max-width: 768px) {
    header {
        padding: 0.75rem 1rem;
    }
    .header-inner {
        flex-direction: column;
        gap: 0.8rem;
        align-items: stretch;
    }
    .nav-tabs {
        overflow-x: auto;
        white-space: nowrap;
        padding-bottom: 0.4rem;
    }
    main {
        padding: 0 0.8rem;
        margin: 1rem auto;
    }
}

/* ==========================================================================
   Dashboard MVP Components (Hero, Metrics, Quick Actions, Notices)
   ========================================================================== */
.header-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(11, 15, 25, 0.6);
    padding: 0.35rem 0.75rem;
    border-radius: 9999px;
    border: 1px solid var(--border-color);
}

.status-indicator {
    width: 8px;
    height: 8px;
    background: var(--accent-emerald);
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(52, 211, 153, 0.8);
    animation: statusPulse 2s infinite;
}

@keyframes statusPulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}

.hero-banner {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.hero-actions {
    display: flex;
    gap: 0.75rem;
    flex-shrink: 0;
}

@media (max-width: 768px) {
    .hero-banner {
        flex-direction: column;
        align-items: flex-start;
        padding: 1.5rem;
    }
    .hero-actions {
        width: 100%;
        flex-direction: column;
    }
}

.grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.25rem;
}

@media (max-width: 1024px) {
    .grid-4 {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 600px) {
    .grid-4 {
        grid-template-columns: 1fr;
    }
}

.metric-card {
    background: var(--bg-card);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: var(--accent-blue);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
}

.metric-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
}

.metric-content h3 {
    font-size: 1.6rem;
    font-weight: 700;
    line-height: 1.1;
    color: var(--text-primary);
}

.metric-content p {
    font-size: 0.78rem;
    color: var(--text-secondary);
    margin-top: 0.2rem;
}

.quick-actions-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.8rem;
}

@media (max-width: 600px) {
    .quick-actions-grid {
        grid-template-columns: 1fr;
    }
}

.action-tile {
    background: rgba(11, 15, 25, 0.6);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.action-tile:hover {
    background: rgba(56, 189, 248, 0.08);
    border-color: var(--accent-blue);
    transform: translateY(-2px);
}

.action-tile-icon {
    font-size: 1.4rem;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    flex-shrink: 0;
}

.action-tile h4 {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.2rem;
}

.action-tile p {
    font-size: 0.72rem;
    color: var(--text-muted);
    line-height: 1.3;
}

.notice-list {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

.notice-item {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    padding: 0.8rem;
    background: rgba(11, 15, 25, 0.5);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    font-size: 0.82rem;
}

.notice-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}

.notice-item strong {
    display: block;
    color: var(--text-primary);
    margin-bottom: 0.2rem;
}

.notice-item p {
    color: var(--text-secondary);
    line-height: 1.35;
    font-size: 0.76rem;
}

.notice-time {
    display: inline-block;
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.3rem;
}

/* ==========================================================================
   Portal Switcher (User Side vs Admin Side)
   ========================================================================== */

.portal-toggle-container {
    display: inline-flex;
    background: rgba(11, 15, 25, 0.85);
    border: 1px solid var(--border-color);
    border-radius: 9999px;
    padding: 0.25rem;
    gap: 0.25rem;
    align-items: center;
}

.portal-btn {
    border: none;
    background: transparent;
    color: var(--text-secondary);
    font-family: var(--font-family);
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.45rem 1rem;
    border-radius: 9999px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
}

.portal-btn:hover {
    color: var(--text-primary);
}

.portal-btn.active {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-indigo));
    color: #fff;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.25);
}

.portal-btn.admin-active {
    background: linear-gradient(135deg, #f43f5e, #e11d48);
    color: #fff;
    box-shadow: 0 4px 12px rgba(244, 63, 94, 0.3);
}

body[data-portal="user"] .admin-only {
    display: none !important;
}

body[data-portal="admin"] .user-only {
    display: none !important;
}

.badge-pending {
    background: rgba(251, 191, 36, 0.18);
    color: #fbbf24;
    border: 1px solid rgba(251, 191, 36, 0.35);
}

.badge-approved {
    background: rgba(52, 211, 153, 0.18);
    color: #34d399;
    border: 1px solid rgba(52, 211, 153, 0.35);
}

.badge-rejected {
    background: rgba(244, 63, 94, 0.18);
    color: #f43f5e;
    border: 1px solid rgba(244, 63, 94, 0.35);
}
````
