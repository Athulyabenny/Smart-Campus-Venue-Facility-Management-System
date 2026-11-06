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
