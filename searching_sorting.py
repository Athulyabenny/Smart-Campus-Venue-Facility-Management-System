"""
Smart Campus Algorithmic Engine: Phase 3 Searching & Sorting
File: core/searching_sorting.py

Features:
1. Linear Search: O(n) sequential scan
2. Binary Search: O(log n) divide-and-conquer on sorted arrays
3. Merge Sort:    O(n log n) stable divide-and-conquer sort
4. Quick Sort:    O(n log n) average in-place partitioning sort
5. Insertion Sort: O(n^2) adaptive sorting for small/nearly-sorted data
6. Conceptual & Empirical Efficiency Comparison
"""

import time
from typing import Any, Callable, List, Optional, Tuple


# =============================================================================
# 1. SEARCHING ALGORITHMS
# =============================================================================

def linear_search(
    arr: List[Any],
    target: Any,
    key_func: Optional[Callable[[Any], Any]] = None
) -> Tuple[int, int]:
    """
    Sequentially searches for target in arr in O(n) time.
    Returns: (found_index: int, comparisons_count: int)
    If not found, found_index is -1.
    """
    comparisons = 0
    for idx, item in enumerate(arr):
        comparisons += 1
        val = key_func(item) if key_func else item
        if val == target:
            return idx, comparisons
    return -1, comparisons


def binary_search(
    arr: List[Any],
    target: Any,
    key_func: Optional[Callable[[Any], Any]] = None
) -> Tuple[int, int]:
    """
    Divides search space in half in O(log n) time.
    PRECONDITION: arr must already be sorted in ascending order of key_func.
    Returns: (found_index: int, comparisons_count: int)
    If not found, found_index is -1.
    """
    low = 0
    high = len(arr) - 1
    comparisons = 0

    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        val = key_func(arr[mid]) if key_func else arr[mid]

        if val == target:
            return mid, comparisons
        elif val < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1, comparisons


# =============================================================================
# 2. SORTING ALGORITHMS
# =============================================================================

def merge_sort(
    arr: List[Any],
    key_func: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False
) -> List[Any]:
    """
    Stable divide-and-conquer sorting algorithm in O(n log n) time and O(n) space.
    Returns a new sorted list.
    """
    if len(arr) <= 1:
        return list(arr)

    mid = len(arr) // 2
    left_sorted = merge_sort(arr[:mid], key_func, reverse)
    right_sorted = merge_sort(arr[mid:], key_func, reverse)

    return _merge(left_sorted, right_sorted, key_func, reverse)


def _merge(
    left: List[Any],
    right: List[Any],
    key_func: Optional[Callable[[Any], Any]],
    reverse: bool
) -> List[Any]:
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        val_l = key_func(left[i]) if key_func else left[i]
        val_r = key_func(right[j]) if key_func else right[j]

        condition = (val_l > val_r) if reverse else (val_l <= val_r)
        if condition:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(
    arr: List[Any],
    key_func: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False
) -> List[Any]:
    """
    In-place divide-and-conquer sorting with Lomuto partitioning.
    Average Time: O(n log n). Worst-case: O(n^2).
    Returns a new sorted list.
    """
    copy_arr = list(arr)
    _quick_sort_helper(copy_arr, 0, len(copy_arr) - 1, key_func, reverse)
    return copy_arr


def _quick_sort_helper(
    arr: List[Any],
    low: int,
    high: int,
    key_func: Optional[Callable[[Any], Any]],
    reverse: bool
) -> None:
    if low < high:
        p_idx = _partition(arr, low, high, key_func, reverse)
        _quick_sort_helper(arr, low, p_idx - 1, key_func, reverse)
        _quick_sort_helper(arr, p_idx + 1, high, key_func, reverse)


def _partition(
    arr: List[Any],
    low: int,
    high: int,
    key_func: Optional[Callable[[Any], Any]],
    reverse: bool
) -> int:
    pivot_val = key_func(arr[high]) if key_func else arr[high]
    i = low - 1

    for j in range(low, high):
        curr_val = key_func(arr[j]) if key_func else arr[j]
        condition = (curr_val > pivot_val) if reverse else (curr_val <= pivot_val)
        if condition:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def insertion_sort(
    arr: List[Any],
    key_func: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False
) -> List[Any]:
    """
    Adaptive in-place sorting in O(n^2) worst case, O(n) best case (already sorted).
    Returns a new sorted list.
    """
    result = list(arr)
    for i in range(1, len(result)):
        current = result[i]
        curr_val = key_func(current) if key_func else current
        j = i - 1

        while j >= 0:
            compare_val = key_func(result[j]) if key_func else result[j]
            condition = (compare_val < curr_val) if reverse else (compare_val > curr_val)
            if condition:
                result[j + 1] = result[j]
                j -= 1
            else:
                break
        result[j + 1] = current

    return result


# =============================================================================
# 3. PERFORMANCE & COMPLEXITY COMPARISON
# =============================================================================

def compare_sorting_algorithms(
    data: Any = None,
    key_func: Optional[Callable[[Any], Any]] = None,
    runs: int = 3,
    sample_size: Optional[int] = None
) -> dict:
    """Benchmark the sorting algorithms on supplied records or sample data.

    ``sample_size`` preserves the original generated-data API. Callers may also
    pass records, a key function, and a repeat count to benchmark real data.
    """
    import random

    if isinstance(data, int):
        sample_size = data
        data = None

    if data is None:
        size = 1000 if sample_size is None else max(0, sample_size)
        rng = random.Random(42)
        items = [rng.randint(1, 10000) for _ in range(size)]
        actual_key_func = None
    else:
        items = list(data)
        size = len(items)
        actual_key_func = key_func

    run_count = max(1, int(runs))

    class ComparisonCounter:
        count = 0
        def __init__(self, val):
            self.val = val
        def __lt__(self, other):
            ComparisonCounter.count += 1
            return self.val < other.val
        def __le__(self, other):
            ComparisonCounter.count += 1
            return self.val <= other.val
        def __gt__(self, other):
            ComparisonCounter.count += 1
            return self.val > other.val
        def __ge__(self, other):
            ComparisonCounter.count += 1
            return self.val >= other.val

    def wrapped_key(item):
        raw_val = actual_key_func(item) if actual_key_func else item
        return ComparisonCounter(raw_val)

    algorithms = [
        ("Merge Sort", merge_sort),
        ("Quick Sort", quick_sort),
        ("Insertion Sort", insertion_sort),
    ]

    bench_stats = {}
    for name, algorithm in algorithms:
        elapsed = []
        comp_count = 0
        for r in range(run_count):
            ComparisonCounter.count = 0
            started = time.perf_counter()
            algorithm(items, key_func=wrapped_key)
            elapsed.append((time.perf_counter() - started) * 1000)
            if r == 0:
                comp_count = ComparisonCounter.count
        average_ms = sum(elapsed) / len(elapsed)
        bench_stats[name] = {
            "avg_ms": round(average_ms, 4),
            "comparisons": comp_count
        }

    results_list = [
        {
            "algorithm": "Merge Sort",
            "time_ms": bench_stats["Merge Sort"]["avg_ms"],
            "avg_ms": bench_stats["Merge Sort"]["avg_ms"],
            "comparisons": bench_stats["Merge Sort"]["comparisons"],
            "best_case": "O(n log n)",
            "average_case": "O(n log n)",
            "worst_case": "O(n log n)",
            "space": "O(n)",
            "stable": True
        },
        {
            "algorithm": "Quick Sort",
            "time_ms": bench_stats["Quick Sort"]["avg_ms"],
            "avg_ms": bench_stats["Quick Sort"]["avg_ms"],
            "comparisons": bench_stats["Quick Sort"]["comparisons"],
            "best_case": "O(n log n)",
            "average_case": "O(n log n)",
            "worst_case": "O(n^2)",
            "space": "O(log n)",
            "stable": False
        },
        {
            "algorithm": "Insertion Sort",
            "time_ms": bench_stats["Insertion Sort"]["avg_ms"],
            "avg_ms": bench_stats["Insertion Sort"]["avg_ms"],
            "comparisons": bench_stats["Insertion Sort"]["comparisons"],
            "best_case": "O(n)",
            "average_case": "O(n^2)",
            "worst_case": "O(n^2)",
            "space": "O(1)",
            "stable": True
        }
    ]

    response = {
        "sample_size": size,
        "runs": run_count,
        "results": results_list,
        "Merge Sort": results_list[0],
        "Quick Sort": results_list[1],
        "Insertion Sort": results_list[2],
    }
    return response
