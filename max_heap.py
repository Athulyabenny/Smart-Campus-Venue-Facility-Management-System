"""
Smart Campus Algorithmic Engine: Custom Binary Max-Heap / Priority Queue
File: core/max_heap.py

Features:
- Pure array-based Binary Max-Heap (0-indexed).
- Zero external DSA libraries (no heapq).
- Dynamic priority updates in O(log n) via internal position hash-map (id -> index).
- Time Complexity:
    * Insert: O(log n)
    * Extract-Max: O(log n)
    * Peek: O(1)
    * Update Priority / Remove: O(log n)
    * Heapify (Build Heap): O(n)
"""

from typing import Any, Callable, Dict, List, Optional


class HeapItem:
    """Represents an element in the Priority Queue."""

    def __init__(self, item_id: str, priority: float, data: Any = None):
        self.item_id: str = item_id
        self.priority: float = priority
        self.data: Any = data

    def __repr__(self) -> str:
        return f"HeapItem(id='{self.item_id}', priority={self.priority:.1f})"


class MaxHeap:
    """
    Custom Binary Max-Heap for Emergency and Volunteer Task Prioritization.
    Maintains max-heap property: parent.priority >= children.priority.
    """

    def __init__(self):
        self._heap: List[HeapItem] = []
        self._pos_map: Dict[str, int] = {}  # item_id -> index in _heap

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    # -------------------------------------------------------------------------
    # Index calculations
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Sift operations
    # -------------------------------------------------------------------------

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent_idx = self._parent(index)
            if self._heap[index].priority > self._heap[parent_idx].priority:
                self._swap(index, parent_idx)
                index = parent_idx
            else:
                break

    def _sift_down(self, index: int) -> None:
        n = len(self._heap)
        while True:
            largest = index
            left = self._left_child(index)
            right = self._right_child(index)

            if left < n and self._heap[left].priority > self._heap[largest].priority:
                largest = left
            if right < n and self._heap[right].priority > self._heap[largest].priority:
                largest = right

            if largest != index:
                self._swap(index, largest)
                index = largest
            else:
                break

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def insert(self, item_id: str, priority: float, data: Any = None) -> None:
        """
        Inserts a new incident/task into the Max-Heap in O(log n).
        If an item with item_id already exists, updates its priority instead.
        """
        if item_id in self._pos_map:
            self.update_priority(item_id, priority, data)
            return

        item = HeapItem(item_id=item_id, priority=priority, data=data)
        self._heap.append(item)
        new_index = len(self._heap) - 1
        self._pos_map[item_id] = new_index
        self._sift_up(new_index)

    def peek(self) -> Optional[HeapItem]:
        """Returns the highest-priority incident without removing it in O(1)."""
        if not self._heap:
            return None
        return self._heap[0]

    def extract_max(self) -> Optional[HeapItem]:
        """
        Pops and returns the highest priority incident in O(log n).
        Re-establishes the max-heap property via sift-down.
        """
        if not self._heap:
            return None

        max_item = self._heap[0]
        last_item = self._heap.pop()
        del self._pos_map[max_item.item_id]

        if self._heap:
            self._heap[0] = last_item
            self._pos_map[last_item.item_id] = 0
            self._sift_down(0)

        return max_item

    def update_priority(self, item_id: str, new_priority: float, data: Any = None) -> bool:
        """
        Dynamically adjusts an incident's priority in O(log n) using position lookup.
        """
        if item_id not in self._pos_map:
            return False

        index = self._pos_map[item_id]
        old_priority = self._heap[index].priority
        self._heap[index].priority = new_priority
        if data is not None:
            self._heap[index].data = data

        if new_priority > old_priority:
            self._sift_up(index)
        elif new_priority < old_priority:
            self._sift_down(index)

        return True

    def remove(self, item_id: str) -> Optional[HeapItem]:
        """Removes an arbitrary item from the heap in O(log n)."""
        if item_id not in self._pos_map:
            return None

        index = self._pos_map[item_id]
        target_item = self._heap[index]
        last_item = self._heap.pop()
        del self._pos_map[item_id]

        if index < len(self._heap):
            self._heap[index] = last_item
            self._pos_map[last_item.item_id] = index
            # May need to sift up or sift down depending on value
            parent_idx = self._parent(index)
            if index > 0 and self._heap[index].priority > self._heap[parent_idx].priority:
                self._sift_up(index)
            else:
                self._sift_down(index)

        return target_item

    def get_items_sorted(self) -> List[HeapItem]:
        """Returns a snapshot of all elements ordered by priority (highest first) without mutating self."""
        clone = MaxHeap()
        for item in self._heap:
            clone.insert(item.item_id, item.priority, item.data)

        sorted_list: List[HeapItem] = []
        while not clone.is_empty():
            sorted_list.append(clone.extract_max())
        return sorted_list

    def to_list(self) -> List[dict]:
        """Returns list of items serialized for API and UI display."""
        return [
            {
                "id": item.item_id,
                "priority": item.priority,
                "data": getattr(item.data, "to_dict", lambda: item.data)() if item.data else None
            }
            for item in self._heap
        ]

    def print_ascii_heap(self) -> str:
        """Visualizes heap tree level-by-level for viva demonstration."""
        if not self._heap:
            return "<Empty Max-Heap>"

        lines = ["=== Binary Max-Heap Tree Structure ==="]
        level = 0
        nodes_in_level = 1
        i = 0
        n = len(self._heap)

        while i < n:
            level_items = []
            for _ in range(nodes_in_level):
                if i < n:
                    item = self._heap[i]
                    level_items.append(f"[{item.item_id}: score={item.priority:.1f}]")
                    i += 1
                else:
                    break
            lines.append(f"Level {level}: " + "  ".join(level_items))
            nodes_in_level *= 2
            level += 1

        return "\n".join(lines)
