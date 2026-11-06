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
