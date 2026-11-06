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
