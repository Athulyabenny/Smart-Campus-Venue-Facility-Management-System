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
