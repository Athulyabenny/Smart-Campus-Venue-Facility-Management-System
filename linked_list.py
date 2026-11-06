"""
Smart Campus Algorithmic Engine: Phase 1 Linear Data Structures
File: core/linked_list.py

Custom Singly Linked List for student data storage and administration.
Implements pointer-based node architecture with zero high-level list library shortcuts.

Time Complexities:
    * Insert at Front (Head): O(1)
    * Insert at Rear (Tail):  O(1) (Maintained via tail pointer)
    * Insert at Position k:   O(n)
    * Delete Front:           O(1)
    * Delete Rear:            O(n)
    * Delete by Key / ID:     O(n)
    * Delete at Position k:   O(n)
    * Search / Traverse:      O(n)
    * In-Place Reversal:      O(n)
"""

from typing import Any, Callable, Generator, List, Optional


class Node:
    """A single node in the Singly Linked List."""

    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional["Node"] = None

    def __repr__(self) -> str:
        return f"Node({self.data})"


class SinglyLinkedList:
    """
    Textbook-grade Singly Linked List with head and tail pointers.
    Maintains size counter for O(1) length queries.
    """

    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.head is None

    # -------------------------------------------------------------------------
    # Insertion Operations
    # -------------------------------------------------------------------------

    def insert_front(self, data: Any) -> None:
        """Inserts a new element at the beginning (head) in O(1)."""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        if self.tail is None:
            self.tail = new_node
        self._size += 1

    def insert_rear(self, data: Any) -> None:
        """Inserts a new element at the end (tail) in O(1) using tail pointer."""
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def insert_at(self, index: int, data: Any) -> bool:
        """
        Inserts an element at a specific 0-based index in O(n).
        Returns True if successful, False if index is out of bounds.
        """
        if index < 0 or index > self._size:
            return False

        if index == 0:
            self.insert_front(data)
            return True
        if index == self._size:
            self.insert_rear(data)
            return True

        new_node = Node(data)
        curr = self.head
        for _ in range(index - 1):
            assert curr is not None
            curr = curr.next

        assert curr is not None
        new_node.next = curr.next
        curr.next = new_node
        self._size += 1
        return True

    # -------------------------------------------------------------------------
    # Deletion Operations
    # -------------------------------------------------------------------------

    def delete_front(self) -> Optional[Any]:
        """Removes and returns the front element in O(1)."""
        if self.head is None:
            return None

        removed_data = self.head.data
        self.head = self.head.next
        self._size -= 1

        if self.head is None:
            self.tail = None

        return removed_data

    def delete_rear(self) -> Optional[Any]:
        """Removes and returns the rear element in O(n)."""
        if self.head is None:
            return None

        if self.head == self.tail:
            removed_data = self.head.data
            self.head = None
            self.tail = None
            self._size = 0
            return removed_data

        curr = self.head
        while curr.next != self.tail:
            assert curr.next is not None
            curr = curr.next

        assert self.tail is not None
        removed_data = self.tail.data
        curr.next = None
        self.tail = curr
        self._size -= 1
        return removed_data

    def delete_at(self, index: int) -> Optional[Any]:
        """Removes element at specific 0-based index in O(n)."""
        if index < 0 or index >= self._size:
            return None

        if index == 0:
            return self.delete_front()
        if index == self._size - 1:
            return self.delete_rear()

        curr = self.head
        for _ in range(index - 1):
            assert curr is not None
            curr = curr.next

        assert curr is not None and curr.next is not None
        removed_data = curr.next.data
        curr.next = curr.next.next
        self._size -= 1
        return removed_data

    def delete_by_key(self, predicate: Callable[[Any], bool]) -> Optional[Any]:
        """
        Deletes the first node matching predicate(data) == True in O(n).
        Returns the removed data or None if not found.
        """
        if self.head is None:
            return None

        if predicate(self.head.data):
            return self.delete_front()

        prev = self.head
        curr = self.head.next

        while curr is not None:
            if predicate(curr.data):
                removed_data = curr.data
                prev.next = curr.next
                if curr == self.tail:
                    self.tail = prev
                self._size -= 1
                return removed_data
            prev = curr
            curr = curr.next

        return None

    # -------------------------------------------------------------------------
    # Search, Traversal & Utilities
    # -------------------------------------------------------------------------

    def search(self, predicate: Callable[[Any], bool]) -> Optional[Any]:
        """Finds first element where predicate(data) is True in O(n)."""
        curr = self.head
        while curr is not None:
            if predicate(curr.data):
                return curr.data
            curr = curr.next
        return None

    def get_at(self, index: int) -> Optional[Any]:
        """Retrieves data at 0-based index in O(n)."""
        if index < 0 or index >= self._size:
            return None
        curr = self.head
        for _ in range(index):
            assert curr is not None
            curr = curr.next
        return curr.data if curr else None

    def reverse(self) -> None:
        """Reverses the linked list in-place in O(n) time and O(1) space."""
        prev = None
        curr = self.head
        self.tail = self.head

        while curr is not None:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node

        self.head = prev

    def to_list(self) -> List[Any]:
        """Extracts elements to a standard Python list for serialisation."""
        result = []
        curr = self.head
        while curr is not None:
            result.append(curr.data)
            curr = curr.next
        return result

    def __iter__(self) -> Generator[Any, None, None]:
        curr = self.head
        while curr is not None:
            yield curr.data
            curr = curr.next

    def display(self) -> str:
        """Returns visual pointer chain representation for CLI & debugging."""
        if self.head is None:
            return "[Empty List] -> None"

        elements = []
        curr = self.head
        while curr is not None:
            # Format data cleanly
            label = getattr(curr.data, "student_id", str(curr.data))
            elements.append(f"[{label}]")
            curr = curr.next
        return " -> ".join(elements) + " -> None"
