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
