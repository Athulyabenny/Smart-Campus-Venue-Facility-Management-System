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
