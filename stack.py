"""
Smart Campus Algorithmic Engine: Phase 1 Linear Data Structures
File: core/stack.py

Custom Node-based Linked Stack (LIFO: Last In, First Out).
Implements pure dynamic node chaining with zero fixed array size bounds.

Time Complexities:
    * Push:     O(1)
    * Pop:      O(1)
    * Peek:     O(1)
    * Is Empty: O(1)
    * Size:     O(1)
"""

from typing import Any, List, Optional


class StackNode:
    """Node in the Linked Stack."""

    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional["StackNode"] = None

    def __repr__(self) -> str:
        return f"StackNode({self.data})"


class LinkedStack:
    """
    Textbook-grade Linked Stack implementation.
    Top of stack corresponds to the head of the linked chain.
    """

    def __init__(self):
        self.top_node: Optional[StackNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.top_node is None

    def push(self, data: Any) -> None:
        """Pushes an element onto the top of the stack in O(1)."""
        new_node = StackNode(data)
        new_node.next = self.top_node
        self.top_node = new_node
        self._size += 1

    def pop(self) -> Any:
        """
        Pops and returns the top element from the stack in O(1).
        Raises IndexError if the stack is empty.
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")

        assert self.top_node is not None
        popped_data = self.top_node.data
        self.top_node = self.top_node.next
        self._size -= 1
        return popped_data

    def peek(self) -> Any:
        """
        Returns the top element without removing it in O(1).
        Raises IndexError if the stack is empty.
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")

        assert self.top_node is not None
        return self.top_node.data

    def to_list(self) -> List[Any]:
        """Returns items from top to bottom."""
        result = []
        curr = self.top_node
        while curr is not None:
            result.append(curr.data)
            curr = curr.next
        return result

    def display(self) -> str:
        """Visual representation of stack for viva demos."""
        if self.is_empty():
            return "<Empty Stack>"

        items = self.to_list()
        lines = ["--- TOP OF STACK ---"]
        for item in items:
            lines.append(f"  | {item} |")
        lines.append("--- BOTTOM OF STACK ---")
        return "\n".join(lines)
