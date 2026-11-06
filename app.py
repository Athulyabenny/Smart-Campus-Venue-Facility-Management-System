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
