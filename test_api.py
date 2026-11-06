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
