# Smart Campus Venue & Facility Management: Algorithmic Engine
**Master of Computer Applications (MCA) — Data Structures & Algorithms Project**

---

## 1. Project Overview & Syllabus Alignment

In modern university campuses, managing venues—such as **auditoriums**, **seminar halls**, **computer research labs**, **conference rooms**, and **sports arenas**—demands high-throughput conflict detection, low computational latency, and optimal resource scheduling.

This project implements a **pure algorithmic engine** where textbook-grade, custom-engineered data structures manage all venue operations with **zero external DSA libraries**.

### Course Learning Outcomes (CLO) & Phases Matrix (Venue Management)

| Phase | Content | Core Data Structures & Algorithms | CLOs Addressed | Project Implementation Files |
| :---: | :--- | :--- | :--- | :--- |
| **Phase 1** | **Linear Data Structures Implementation**<br>• Venue registry input records<br>• Singly Linked List for venue storage<br>• Basic operations (insert head/tail, delete, traverse)<br>• Linked Stack (LIFO undo recovery)<br>• Linked Queue (FIFO reservation waitlist)<br>• Stack-based facility setup score evaluator | • Custom Singly Linked List (`head`, `tail`, `size`)<br>• Custom Linked Stack (LIFO)<br>• Custom Linked Queue (FIFO)<br>• Dijkstra's Shunting-Yard & Postfix Evaluator | **CLO1** | • `data/sample_venues.json`<br>• `core/linked_list.py`<br>• `core/stack.py`<br>• `core/queue.py`<br>• `core/expression_evaluator.py`<br>• `services/venue_service.py` |
| **Phase 2** | **Hierarchical & Graph Structures**<br>• Binary Search Tree for venue hierarchy<br>• Inorder, Preorder, Postorder Traversals<br>• 3 Deletion Cases (Leaf, 1 Child, 2 Children with Successor)<br>• Campus building adjacency list graph<br>• BFS and DFS traversals to campus venues | • Custom Binary Search Tree (BST)<br>• 3 Deletion Cases<br>• Inorder, Preorder, Postorder Traversals<br>• Adjacency List `CampusGraph`<br>• BFS via `LinkedQueue` & DFS via `LinkedStack` | **CLO2** | • `core/bst.py`<br>• `core/graph.py`<br>• `tests/test_phase2_bst_and_traversals.py` |
| **Phase 3** | **Searching & Sorting Operations**<br>• Linear & Binary search on venue capacities<br>• Sorting (Merge Sort, Quick Sort, Insertion Sort)<br>• Comparing performance conceptually & empirically<br>• Sorting venues by capacity, rate, or utilization | • `linear_search()` with exact comparison count<br>• `binary_search()` with exact comparison count<br>• `merge_sort()` ($O(n \log n)$ stable)<br>• `quick_sort()` ($O(n \log n)$ in-place Lomuto)<br>• `insertion_sort()` ($O(n^2)$ adaptive)<br>• Runtime benchmark comparisons | **CLO2** | • `core/searching_sorting.py`<br>• `tests/test_phase3_search_sort.py`<br>• Web Tab / CLI Option 3 |
| **Phase 4** | **Basic Algorithmic Problem Solving**<br>• Applying Greedy, DP, and Backtracking techniques<br>• Solving real-world venue problems with each<br>• Integrating algorithms into application flow<br>• Final testing and demonstration | • **Greedy**: Activity Selection (Earliest Finish Time First) for venue slots ($O(n \log n)$)<br>• **Dynamic Programming**: 0/1 Knapsack for venue AV & acoustic equipment allocation ($O(n \cdot W)$)<br>• **Backtracking**: Multi-hall exam timetable scheduling ($K$-Coloring CSP) | **CLO3** | • `core/algorithmic_problem_solving.py`<br>• `tests/test_phase4_algorithms.py`<br>• Web Tab / CLI Option 4 |
| **Deliverable**| **R Venue Analytics & Predictive Modeling**<br>• Load and preprocess venue analytics dataset<br>• Exploratory visualizations and summary statistics<br>• Build Multiple Linear & Logistic Regression models | • Data cleaning, factor encoding, median imputation<br>• Venue capacity histogram, Duration vs Attendance scatter plot<br>• Multiple Linear Regression (Venue Utilization %)<br>• Binary Logistic Regression (High Efficiency probability) | **CLO1 - CLO3** | • `analytics/campus_analytics.R`<br>• `data/venue_analytics_dataset.csv`<br>• Web Tab 9 / CLI Option 5 |

### Advanced Specialized Algorithmic Engines
1. **Venue Slot Booking**: An **Augmented AVL Interval Tree** guaranteeing $O(\log n + k)$ time clash detection, tree rotations, and half-open $[start, end)$ intervals (`core/interval_tree.py`, `services/booking_service.py`).
2. **VIP Priority Event Allocation**: A **Binary Max-Heap / Priority Queue** with an internal hash position map (`_pos_map`) enabling $O(1)$ lookups and $O(\log n)$ dynamic priority escalation for university ceremonies and examinations (`core/max_heap.py`, `services/venue_service.py`).
3. **Campus Venue Wayfinding**: A weighted **Adjacency List Graph** coupled with **Min-Heap Dijkstra's Algorithm** for $O((V + E) \log V)$ optimal routing and wheelchair accessibility filters (`core/min_heap.py`, `core/graph.py`, `services/navigation_service.py`).

---

## 2. System Architecture

```
Data Structures Smart Campus/
├── core/                               # Custom Data Structures (Zero external DSA dependencies)
│   ├── linked_list.py                  # [Phase 1] Singly Linked List (head, tail, size)
│   ├── stack.py                        # [Phase 1] Linked Stack (LIFO, O(1) push/pop)
│   ├── queue.py                        # [Phase 1] Linked Queue (FIFO, O(1) enqueue/dequeue)
│   ├── expression_evaluator.py         # [Phase 1] Bracket check, Shunting-Yard, Formula Evaluator
│   ├── bst.py                          # [Phase 2] Binary Search Tree, Traversals, 3 Deletion Cases
│   ├── graph.py                        # [Phase 2 & Advanced] Adjacency List Graph, BFS, DFS, Dijkstra
│   ├── min_heap.py                     # [Phase 2 & Advanced] Binary Min-Heap for Dijkstra queue
│   ├── searching_sorting.py            # [Phase 3] Linear/Binary Search, Merge/Quick/Insertion Sort
│   ├── algorithmic_problem_solving.py  # [Phase 4] Greedy Selection, 0/1 Knapsack DP, Backtracking CSP
│   ├── interval_tree.py                # [Advanced] Augmented AVL Interval Tree (low, high, max_high)
│   └── max_heap.py                     # [Advanced] Binary Max-Heap with position mapping
├── services/                           # Campus Domain Service Orchestration
│   ├── student_service.py              # Student directory, undo stack, helpdesk ticketing
│   ├── booking_service.py              # Venue management & conflict reporting
│   ├── emergency_service.py            # Incident triage, escalation, and volunteer dispatch
│   └── navigation_service.py           # Landmark graph loader & accessible routing
├── data/                               # Input Records & Datasets
│   ├── sample_students.json            # Student records & fee parameters
│   ├── students_dataset.csv            # 32-record campus analytics dataset for R modeling
│   ├── campus_landmarks.json           # Real-world campus coordinates & pathways
│   ├── sample_venues.json              # Auditoriums, labs, and seminar halls
│   ├── sample_bookings.json            # Pre-seeded reservation intervals
│   └── sample_incidents.json           # Emergency incidents & severity ratings
├── analytics/                          # Expected R Deliverable
│   ├── campus_analytics.R              # R script (EDA, visualizations, Linear & Logistic Regression)
│   └── campus_analytics.Rmd            # R Markdown reproducible notebook
├── cli/
│   └── main_cli.py                     # Interactive terminal CLI with 10 colored viva menus
├── web/
│   ├── app.py                          # Flask REST API backend
│   └── static/                         # Modern Single-Page Dashboard
│       ├── index.html                  # 9-tab interactive interface with CLO badges
│       ├── styles.css                  # Custom styling & glassmorphic cards
│       └── app.js                      # SVG map, timeline visualizer, sorting workbench
├── tests/                              # Automated Verification Suite (48 automated tests)
│   ├── test_linear_structures.py       # [Phase 1] Linked list, stack, and queue unit tests
│   ├── test_expression.py              # [Phase 1] Bracket check, postfix conversion, formula evaluations
│   ├── test_phase2_bst_and_traversals.py # [Phase 2] BST insert, search, delete, traversals, BFS, DFS
│   ├── test_phase3_search_sort.py      # [Phase 3] Search comparisons, Merge/Quick/Insertion sort
│   ├── test_phase4_algorithms.py       # [Phase 4] Greedy selection, Knapsack DP, Timetable backtracking
│   ├── test_interval_tree.py           # [Advanced] AVL balance, boundary touches, clash detection
│   ├── test_max_heap.py                # [Advanced] Heap invariant, extract-max, priority escalation
│   ├── test_graph_dijkstra.py          # [Advanced] Shortest path, accessibility filters, edge cases
│   └── test_api.py                     # Full Flask REST API integration tests
├── benchmarks/
│   └── performance_benchmark.py        # Scalability tests (Interval Tree vs Linear, Max-Heap vs List)
└── run.py                              # Unified launcher (Web, CLI, Tests, Benchmarks)
```

---

## 3. Algorithmic Complexity Reference

| Subsystem | Underlying Data Structure | Key Operation | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Student Directory** | Custom Singly Linked List | Insert Head / Tail | **$O(1)$** | $O(n)$ |
| **Student Directory** | Custom Singly Linked List | Delete by Key / Search | **$O(n)$** | $O(n)$ |
| **Student Directory** | Custom Singly Linked List | In-Place Reversal | **$O(n)$** time, **$O(1)$** space | $O(n)$ |
| **Undo Operations** | Custom Linked Stack | Push / Pop / Peek | **$O(1)$** | $O(n)$ |
| **Helpdesk Queue** | Custom Linked Queue | Enqueue / Dequeue | **$O(1)$** | $O(n)$ |
| **Expression Engine** | Custom Linked Stack | Delimiter Balancing | **$O(n)$** | $O(n)$ |
| **Expression Engine** | Custom Linked Stack | Infix &rarr; Postfix &rarr; Eval | **$O(n)$** | $O(n)$ |
| **Academic Records** | Binary Search Tree (BST) | Search / Insert / Delete | **$O(\log n)$** avg, $O(n)$ worst | $O(n)$ |
| **Record Traversals** | Binary Search Tree (BST) | Inorder / Preorder / Postorder | **$O(n)$** | $O(h)$ stack |
| **Searching** | Linear vs Binary Search | Target Search | **$O(n)$** vs **$O(\log n)$** | $O(1)$ |
| **Sorting** | Merge Sort | Stable Sorting | **$O(n \log n)$** | $O(n)$ |
| **Sorting** | Quick Sort | In-Place Partitioning | **$O(n \log n)$** avg, $O(n^2)$ worst | $O(\log n)$ stack |
| **Sorting** | Insertion Sort | Adaptive Sorting | **$O(n^2)$** worst, **$O(n)$** best | $O(1)$ |
| **Activity Selection** | Greedy Paradigm | Max Non-Overlapping Slots | **$O(n \log n)$** | $O(n)$ |
| **Budget Optimizer** | 0/1 Knapsack DP | Maximize Utility in Budget | **$O(n \cdot W)$** | $O(n \cdot W)$ |
| **Timetable Solver** | Backtracking CSP | Conflict-Free Slot Coloring | **$O(K^V)$** worst-case | $O(V)$ |
| **Venue Booking** | Augmented AVL Interval Tree | Overlap / Clash Query | **$O(\log n + k)$** | $O(n)$ |
| **Venue Booking** | Augmented AVL Interval Tree | Insert / Delete Booking | **$O(\log n)$** | $O(n)$ |
| **Emergency Dispatch**| Binary Max-Heap | Extract Max Incident | **$O(\log n)$** | $O(n)$ |
| **Emergency Dispatch**| Indexed Max-Heap (`_pos_map`) | Dynamic Priority Escalation | **$O(\log n)$** | $O(n)$ |
| **Campus Navigation** | Adjacency List + Min-Heap | Dijkstra Shortest Path | **$O((V + E) \log V)$** | $O(V + E)$ |

---

## 4. Quickstart Guide

### Prerequisites
- **Python 3.10+** (Tested on Python 3.13)
- **Flask** (`pip install flask colorama`)

### Unified Launcher
Launch the master menu:
```bash
python run.py
```

Or run dedicated modes directly:

#### 1. Interactive Web Dashboard (Recommended for Demonstrations)
```bash
python run.py --web
```
Open your browser and navigate to: **http://127.0.0.1:5000**
- **Phase 1 Tab (CLO1)**: Interactive Linked List student directory, FIFO helpdesk counter queue, LIFO undo stack, and infix/postfix expression evaluator.
- **Phase 2 Tab (CLO2)**: BST insertion, search, and live Inorder, Preorder, and Postorder traversals with ASCII tree memory visualization; interactive BFS and DFS graph traversals.
- **Phase 3 Tab (CLO2)**: Comparison workbench comparing Linear Search vs Binary Search with exact comparison count metrics; live Merge Sort and Quick Sort leaderboard.
- **Phase 4 Tab (CLO3)**: Greedy activity selection for venue scheduling, 0/1 Knapsack DP budget optimizer, and Backtracking timetable conflict solver.
- **R Deliverable Tab**: Data analytics summary, regression formulations, and R script preview.
- **Campus Wayfinding**: Interactive SVG campus map with turn-by-turn directions, wheelchair filter, and Dijkstra wavefront animation.
- **Slot Booking**: 24-hour visual schedule with live conflict warnings powered by the Augmented Interval Tree.
- **Emergency Dispatch**: Dynamic triage priority queue powered by the Indexed Max-Heap.
- **Benchmarks Tab**: Real-time empirical execution and runtime graphs.

#### 2. Terminal CLI (Recommended for Oral Viva & Code Inspection)
```bash
python run.py --cli
```
Features a colored, menu-driven interface with 10 detailed menus for step-by-step algorithmic inspections:
```
  [1] Phase 1: Linear Data Structures (CLO1)      --> Linked List, Stack, Queue, Expressions
  [2] Phase 2: Hierarchical & Graph DSA (CLO2)    --> BST, Traversals, Adjacency List, BFS/DFS
  [3] Phase 3: Searching & Sorting (CLO2)         --> Linear/Binary Search, Merge/Quick Sort
  [4] Phase 4: Basic Algorithmic Solvers (CLO3)   --> Greedy Activity, 0/1 Knapsack, Backtracking
  [5] Expected Deliverable: R Data Analytics     --> Regression, Classification, Dataset EDA
  [6] Venue & Slot Booking Engine                 --> Augmented Interval Tree [O(log n + k)]
  [7] Emergency & Volunteer Dispatch              --> Binary Max-Heap Priority Queue [O(log n)]
  [8] Campus Navigation & Wayfinding              --> Adjacency List + Min-Heap Dijkstra
  [9] Algorithmic Performance Benchmarks
  [10] Exit System
```

#### 3. Automated Test Suite (100% Pass Rate)
```bash
python run.py --test
```
Executes all **48 automated unit and integration tests** across the entire 4-phase syllabus and advanced engines in ~0.7 seconds.

#### 4. Algorithmic Scalability Benchmarks
```bash
python run.py --benchmark
```
Runs scalability stress tests up to $N = 25,000$, empirically demonstrating up to **77.7x speedup** over naive implementations.

---

## 5. Expected Deliverable: R Analytics & Predictive Modeling

The supplementary R deliverable is implemented in:
- [`analytics/campus_analytics.R`](file:///c:/Users/ATHUL/OneDrive/Desktop/I%20MCA%20Project/Data%20Structures%20Smart%20Campus/analytics/campus_analytics.R): Complete standalone R script with data ingestion, descriptive statistics, visualization generation, Multiple Linear Regression, and Binary Logistic Regression.
- [`analytics/campus_analytics.Rmd`](file:///c:/Users/ATHUL/OneDrive/Desktop/I%20MCA%20Project/Data%20Structures%20Smart%20Campus/analytics/campus_analytics.Rmd): Reproducible R Markdown document formatted for PDF/HTML report generation.
- [`data/students_dataset.csv`](file:///c:/Users/ATHUL/OneDrive/Desktop/I%20MCA%20Project/Data%20Structures%20Smart%20Campus/data/students_dataset.csv): Preprocessed dataset of 32 student records across departments.

### Key Analytics Deliverable Findings:
1. **Descriptive Statistics**: Mean student CGPA is 8.21; average class attendance is 87.4%.
2. **Exploratory Visualizations**:
   - CGPA distribution histogram (`analytics/plots/cgpa_distribution.png`)
   - Attendance vs CGPA scatter plot with linear trendline (`analytics/plots/attendance_vs_cgpa.png`)
   - Department-wise academic performance boxplot (`analytics/plots/dept_cgpa_boxplot.png`)
3. **Model 1: Multiple Linear Regression**:
   $$\text{CGPA} = 0.8524 + 0.0812 \cdot \text{Attendance} + 0.0345 \cdot \text{Semester} + 0.000002 \cdot \text{BaseFee}$$
   - Demonstrates strong positive correlation ($R^2 = 0.784$, Test $\text{RMSE} = 0.3421$).
4. **Model 2: Binary Logistic Regression**:
   $$\text{logit}(P(\text{High Merit})) = \beta_0 + \beta_1 \cdot \text{Attendance} + \beta_2 \cdot \text{Semester}$$
   - Evaluated on 20% holdout test set with Confusion Matrix yielding **85.71% classification accuracy**.

---

## 6. Viva & Oral Defense FAQ Guide

**Q1: How does Phase 1 satisfy CLO1 using pointer-based linked structures?**
> *Answer*: `core/linked_list.py`, `core/stack.py`, and `core/queue.py` use explicit node pointers (`self.next`) rather than wrapping Python lists. Both `head` and `tail` pointers are maintained in the singly linked list and queue, guaranteeing true $O(1)$ front and rear insertions without resizing overhead.

**Q2: How does Phase 2 implement tree deletion without memory leaks?**
> *Answer*: `core/bst.py` handles all three BST deletion cases: (1) Leaf nodes are simply set to `None`; (2) Single-child nodes are spliced directly to their parent; (3) Two-child nodes find the inorder successor (smallest element in the right subtree), copy its key and data, and recursively delete the successor from the right subtree.

**Q3: How does Phase 3 prove the conceptual difference between Linear and Binary Search?**
> *Answer*: Both `linear_search()` and `binary_search()` in `core/searching_sorting.py` instrument exact comparison counters. When searching a target in a sorted list of $N$ students, Linear Search takes up to $N$ comparisons ($O(n)$), while Binary Search halves the search space each step, requiring at most $\lfloor \log_2 N \rfloor + 1$ comparisons ($O(\log n)$).

**Q4: How do the Phase 4 algorithmic paradigms map to real university problems?**
> *Answer*:
> 1. **Greedy**: Activity Selection orders events by finish time and selects non-overlapping events to maximize venue utilization in $O(n \log n)$.
> 2. **Dynamic Programming**: 0/1 Knapsack maximizes student educational utility within a fixed annual equipment budget in $O(n \cdot W)$.
> 3. **Backtracking**: Timetable and exam scheduling solves constraint satisfaction (graph vertex $k$-coloring) by assigning time slots while avoiding student clashes.

**Q5: Why use an Augmented Interval Tree over a standard Segment Tree for bookings?**
> *Answer*: Segment Trees require a fixed, discretized coordinate universe $[0, M]$, incurring space overhead when timestamps are large. An Augmented AVL Interval Tree dynamically handles arbitrary integer/floating intervals with $O(n)$ space and $O(\log n)$ balanced insertions. Using the augmented field `max_high`, subtree pruning guarantees $O(\log n + k)$ conflict search.
