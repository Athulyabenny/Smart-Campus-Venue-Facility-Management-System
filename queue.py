"""
Smart Campus Algorithmic Engine: Phase 1 Linear Data Structures
File: core/queue.py

Custom Node-based Linked Queue (FIFO: First In, First Out).
Implements front and rear pointer architecture with O(1) enqueue and dequeue.

Time Complexities:
    * Enqueue:  O(1) (Rear pointer insertion)
    * Dequeue:  O(1) (Front pointer removal)
    * Peek:     O(1)
    * Is Empty: O(1)
    * Size:     O(1)
"""

from typing import Any, List, Optional


class QueueNode:
    """Node in the Linked Queue."""

    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional["QueueNode"] = None

    def __repr__(self) -> str:
        return f"QueueNode({self.data})"


class LinkedQueue:
    """
    Textbook-grade Linked Queue implementation.
    Enqueues at rear and dequeues from front.
    """

    def __init__(self):
        self.front: Optional[QueueNode] = None
        self.rear: Optional[QueueNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.front is None

    def enqueue(self, data: Any) -> None:
        """Adds an item to the rear of the queue in O(1)."""
        new_node = QueueNode(data)
        if self.rear is None:
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self._size += 1

    def dequeue(self) -> Any:
        """
        Removes and returns the item from the front of the queue in O(1).
        Raises IndexError if the queue is empty.
        """
        if self.is_empty():
            raise IndexError("dequeue from empty queue")

        assert self.front is not None
        removed_data = self.front.data
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self._size -= 1
        return removed_data

    def peek(self) -> Any:
        """
        Returns the item at the front of the queue without removing it in O(1).
        Raises IndexError if the queue is empty.
        """
        if self.is_empty():
            raise IndexError("peek from empty queue")

        assert self.front is not None
        return self.front.data

    def to_list(self) -> List[Any]:
        """Returns list of items from front to rear."""
        result = []
        curr = self.front
        while curr is not None:
            result.append(curr.data)
            curr = curr.next
        return result

    def display(self) -> str:
        """Visual representation of queue for viva demos."""
        if self.is_empty():
            return "<Empty Queue>"

        items = self.to_list()
        formatted = " -> ".join([f"[{item}]" for item in items])
        return f"FRONT -> {formatted} -> REAR"
