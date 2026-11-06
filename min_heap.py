"""
Smart Campus Algorithmic Engine: Custom Binary Min-Heap
File: core/min_heap.py

Features:
- Pure array-based Binary Min-Heap (0-indexed).
- Invariant: parent.priority <= children.priority.
- Used primarily by Dijkstra's shortest path algorithm for O((V + E) log V) execution.
- Supports decrease_key / update in O(log n) via position lookup.
"""

from typing import Any, Dict, List, Optional


class MinHeapItem:
    """Represents an item in the Min-Heap."""

    def __init__(self, item_id: str, priority: float, data: Any = None):
        self.item_id: str = item_id
        self.priority: float = priority
        self.data: Any = data

    def __repr__(self) -> str:
        return f"MinHeapItem(id='{self.item_id}', priority={self.priority:.2f})"


class MinHeap:
    """
    Custom Binary Min-Heap for Dijkstra's Algorithm and shortest path priority queues.
    Zero external libraries used.
    """

    def __init__(self):
        self._heap: List[MinHeapItem] = []
        self._pos_map: Dict[str, int] = {}

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def contains(self, item_id: str) -> bool:
        return item_id in self._pos_map

    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left_child(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right_child(i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._pos_map[self._heap[i].item_id] = i
        self._pos_map[self._heap[j].item_id] = j

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent_idx = self._parent(index)
            if self._heap[index].priority < self._heap[parent_idx].priority:
                self._swap(index, parent_idx)
                index = parent_idx
            else:
                break

    def _sift_down(self, index: int) -> None:
        n = len(self._heap)
        while True:
            smallest = index
            left = self._left_child(index)
            right = self._right_child(index)

            if left < n and self._heap[left].priority < self._heap[smallest].priority:
                smallest = left
            if right < n and self._heap[right].priority < self._heap[smallest].priority:
                smallest = right

            if smallest != index:
                self._swap(index, smallest)
                index = smallest
            else:
                break

    def insert(self, item_id: str, priority: float, data: Any = None) -> None:
        """Inserts an element into the min-heap in O(log n)."""
        if item_id in self._pos_map:
            self.decrease_key(item_id, priority, data)
            return

        item = MinHeapItem(item_id=item_id, priority=priority, data=data)
        self._heap.append(item)
        new_index = len(self._heap) - 1
        self._pos_map[item_id] = new_index
        self._sift_up(new_index)

    def extract_min(self) -> Optional[MinHeapItem]:
        """Extracts the minimum priority item in O(log n)."""
        if not self._heap:
            return None

        min_item = self._heap[0]
        last_item = self._heap.pop()
        del self._pos_map[min_item.item_id]

        if self._heap:
            self._heap[0] = last_item
            self._pos_map[last_item.item_id] = 0
            self._sift_down(0)

        return min_item

    def peek(self) -> Optional[MinHeapItem]:
        """Returns the minimum element without removing it in O(1)."""
        if not self._heap:
            return None
        return self._heap[0]

    def decrease_key(self, item_id: str, new_priority: float, data: Any = None) -> bool:
        """
        Decreases the key/priority of an item in O(log n).
        Crucial for efficient Dijkstra edge relaxation.
        """
        if item_id not in self._pos_map:
            return False

        index = self._pos_map[item_id]
        if new_priority > self._heap[index].priority:
            # If priority increased, sift down
            self._heap[index].priority = new_priority
            if data is not None:
                self._heap[index].data = data
            self._sift_down(index)
        else:
            self._heap[index].priority = new_priority
            if data is not None:
                self._heap[index].data = data
            self._sift_up(index)

        return True
