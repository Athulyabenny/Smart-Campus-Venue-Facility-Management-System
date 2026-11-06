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

