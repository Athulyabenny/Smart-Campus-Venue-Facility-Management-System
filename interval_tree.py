"""
Smart Campus Algorithmic Engine: Custom Augmented Interval Tree
File: core/interval_tree.py

An Augmented AVL Tree storing intervals [low, high) with:
- BST key: low (start time)
- Augmented attribute: max_high = max(self.high, left.max_high, right.max_high)
- Guaranteed AVL balance factor in {-1, 0, 1} with height O(log n)
- Time Complexity:
    * Insertion: O(log n)
    * Deletion:  O(log n)
    * Single Overlap Query: O(log n)
    * All Overlaps Query:  O(log n + k), where k is the number of overlapping intervals
"""

from typing import Any, List, Optional


class IntervalNode:
    """Node in an Augmented AVL Interval Tree."""

    def __init__(self, low: int, high: int, data: Any = None):
        if low >= high:
            raise ValueError(f"Invalid interval: start time ({low}) must be strictly less than end time ({high}).")
        self.low: int = low
        self.high: int = high
        self.data: Any = data
        self.max_high: int = high
        self.height: int = 1
        self.left: Optional["IntervalNode"] = None
        self.right: Optional["IntervalNode"] = None

    def overlaps_with(self, low: int, high: int) -> bool:
        """
        Determines whether [self.low, self.high) overlaps with [low, high).
        Standard half-open interval overlap condition: self.low < high and low < self.high.
        Touching at boundary (e.g. 10-11 and 11-12) does NOT count as clash.
        """
        return self.low < high and low < self.high

    def __repr__(self) -> str:
        data_str = f" ({self.data})" if self.data else ""
        return f"IntervalNode([{self.low}, {self.high}), max={self.max_high}, h={self.height}{data_str})"


class IntervalTree:
    """
    Custom AVL-balanced Interval Tree for venue slot conflict detection.
    Zero external libraries used.
    """

    def __init__(self):
        self.root: Optional[IntervalNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.root is None

    # -------------------------------------------------------------------------
    # AVL Helpers: Height, Max_High recalculation, and Rotations
    # -------------------------------------------------------------------------

    @staticmethod
    def _get_height(node: Optional[IntervalNode]) -> int:
        return node.height if node else 0

    @staticmethod
    def _get_max_high(node: Optional[IntervalNode]) -> int:
        return node.max_high if node else -1

    def _get_balance(self, node: Optional[IntervalNode]) -> int:
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _update_node(self, node: IntervalNode) -> None:
        """Recalculates height and augmented max_high from immediate children."""
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        node.max_high = max(
            node.high,
            self._get_max_high(node.left),
            self._get_max_high(node.right)
        )

    def _rotate_right(self, y: IntervalNode) -> IntervalNode:
        r"""
             y                               x
            / \     Right Rotation          / \
           x   T3   -------------->        T1  y
          / \                                 / \
         T1  T2                              T2  T3
        """
        x = y.left
        assert x is not None
        t2 = x.right

        # Perform rotation
        x.right = y
        y.left = t2

        # Update affected nodes (bottom-up: y first, then x)
        self._update_node(y)
        self._update_node(x)

        return x

    def _rotate_left(self, x: IntervalNode) -> IntervalNode:
        r"""
           x                                 y
          / \       Left Rotation           / \
         T1  y      ------------->         x   T3
            / \                           / \
           T2  T3                        T1  T2
        """
        y = x.right
        assert y is not None
        t2 = y.left

        # Perform rotation
        y.left = x
        x.right = t2

        # Update affected nodes (bottom-up: x first, then y)
        self._update_node(x)
        self._update_node(y)

        return y

    # -------------------------------------------------------------------------
    # Insertion with AVL Rebalancing: O(log n)
    # -------------------------------------------------------------------------

    def insert(self, low: int, high: int, data: Any = None) -> None:
        """Inserts an interval [low, high) with associated data."""
        self.root = self._insert_node(self.root, low, high, data)
        self._size += 1

    def _insert_node(self, node: Optional[IntervalNode], low: int, high: int, data: Any) -> IntervalNode:
        # Standard BST insertion
        if not node:
            return IntervalNode(low, high, data)

        # Order by low; use high as secondary tiebreaker
        if low < node.low or (low == node.low and high < node.high):
            node.left = self._insert_node(node.left, low, high, data)
        else:
            node.right = self._insert_node(node.right, low, high, data)

        # Update height and max_high on ancestor path
        self._update_node(node)

        # AVL Balancing
        balance = self._get_balance(node)

        # Case 1: Left-Left (LL)
        if balance > 1 and node.left and (low < node.left.low or (low == node.left.low and high < node.left.high)):
            return self._rotate_right(node)

        # Case 2: Right-Right (RR)
        if balance < -1 and node.right and (low > node.right.low or (low == node.right.low and high >= node.right.high)):
            return self._rotate_left(node)

        # Case 3: Left-Right (LR)
        if balance > 1 and node.left and (low > node.left.low or (low == node.left.low and high >= node.left.high)):
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Case 4: Right-Left (RL)
        if balance < -1 and node.right and (low < node.right.low or (low == node.right.low and high < node.right.high)):
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # -------------------------------------------------------------------------
    # Deletion with AVL Rebalancing: O(log n)
    # -------------------------------------------------------------------------

    def delete(self, low: int, high: int, data_id: Optional[str] = None) -> bool:
        """
        Deletes the specified interval [low, high).
        Returns True if deleted, False if not found.
        """
        initial_size = self._size
        self.root = self._delete_node(self.root, low, high, data_id)
        return self._size < initial_size

    def _get_min_node(self, node: IntervalNode) -> IntervalNode:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _delete_node(
        self,
        node: Optional[IntervalNode],
        low: int,
        high: int,
        data_id: Optional[str] = None
    ) -> Optional[IntervalNode]:
        if not node:
            return None

        # Locate node
        if low < node.low or (low == node.low and high < node.high):
            node.left = self._delete_node(node.left, low, high, data_id)
        elif low > node.low or (low == node.low and high > node.high):
            node.right = self._delete_node(node.right, low, high, data_id)
        else:
            # Check if this node matches data_id when tiebreaker is needed
            current_id = getattr(node.data, "booking_id", None) if hasattr(node.data, "booking_id") else None
            if data_id is not None and current_id is not None and current_id != data_id:
                # Same interval, but different booking; check right subtree
                node.right = self._delete_node(node.right, low, high, data_id)
                self._update_node(node)
                return node

            # Match found: perform standard BST deletion
            self._size -= 1
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Node with two children: replace with inorder successor
            successor = self._get_min_node(node.right)
            node.low = successor.low
            node.high = successor.high
            node.data = successor.data

            # Delete the successor from right subtree
            self._size += 1
            node.right = self._delete_node(
                node.right,
                successor.low,
                successor.high,
                getattr(successor.data, "booking_id", None) if hasattr(successor.data, "booking_id") else None
            )

        if not node:
            return None

        # Re-update height and max_high
        self._update_node(node)

        # AVL Rebalancing
        balance = self._get_balance(node)

        # LL Case
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)

        # LR Case
        if balance > 1 and self._get_balance(node.left) < 0:
            assert node.left is not None
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # RR Case
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)

        # RL Case
        if balance < -1 and self._get_balance(node.right) > 0:
            assert node.right is not None
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # -------------------------------------------------------------------------
    # Conflict Detection Queries: O(log n) single clash, O(log n + k) all clashes
    # -------------------------------------------------------------------------

    def find_any_overlap(self, low: int, high: int) -> Optional[IntervalNode]:
        """
        CLRS Interval Search: Returns ANY node overlapping with [low, high) in O(log n).
        Returns None if no overlap exists.
        """
        current = self.root
        while current is not None and not current.overlaps_with(low, high):
            if current.left is not None and current.left.max_high > low:
                current = current.left
            else:
                current = current.right
        return current

    def find_all_overlapping(self, low: int, high: int) -> List[IntervalNode]:
        """
        Reports ALL intervals overlapping with [low, high) in O(log n + k) time.
        Subtree pruning guarantees only candidates can be traversed.
        """
        overlaps: List[IntervalNode] = []
        self._find_all_overlapping_recursive(self.root, low, high, overlaps)
        return overlaps

    def _find_all_overlapping_recursive(
        self,
        node: Optional[IntervalNode],
        low: int,
        high: int,
        result: List[IntervalNode]
    ) -> None:
        if node is None:
            return

        # Check current node
        if node.overlaps_with(low, high):
            result.append(node)

        # Prune Left Subtree:
        # Only search left if left child exists AND its max endpoint > query's start time
        if node.left is not None and node.left.max_high > low:
            self._find_all_overlapping_recursive(node.left, low, high, result)

        # Prune Right Subtree:
        # Only search right if current node's start time < query's end time
        if node.low < high and node.right is not None:
            self._find_all_overlapping_recursive(node.right, low, high, result)

    # -------------------------------------------------------------------------
    # Traversals & Visualizers
    # -------------------------------------------------------------------------

    def inorder(self) -> List[IntervalNode]:
        """Returns all intervals in ascending order of start time."""
        result: List[IntervalNode] = []

        def _inorder(node: Optional[IntervalNode]):
            if node:
                _inorder(node.left)
                result.append(node)
                _inorder(node.right)

        _inorder(self.root)
        return result

    def to_dict(self) -> Optional[dict]:
        """Returns a hierarchical JSON-serializable dictionary for Web visualizers."""
        def _build(node: Optional[IntervalNode]):
            if not node:
                return None
            data_val = None
            if node.data:
                if hasattr(node.data, "to_dict"):
                    data_val = node.data.to_dict()
                else:
                    data_val = str(node.data)
            return {
                "low": node.low,
                "high": node.high,
                "max_high": node.max_high,
                "height": node.height,
                "data": data_val,
                "left": _build(node.left),
                "right": _build(node.right)
            }
        return _build(self.root)

    def print_ascii_tree(self) -> str:
        """Generates an ASCII tree representation for terminal demos."""
        if not self.root:
            return "<Empty Interval Tree>"

        lines: List[str] = []

        def _print_node(node: Optional[IntervalNode], prefix: str = "", is_left: bool = True):
            if node is not None:
                title = getattr(node.data, "title", "") if node.data else ""
                tag = f" ({title})" if title else ""
                lines.append(
                    f"{prefix}{'|-- ' if is_left else '\\-- '}"
                    f"[{node.low}, {node.high}) [max={node.max_high}, h={node.height}]{tag}"
                )
                child_prefix = prefix + ("|   " if is_left else "    ")
                if node.left or node.right:
                    if node.left:
                        _print_node(node.left, child_prefix, True)
                    else:
                        lines.append(f"{child_prefix}|-- <None>")
                    if node.right:
                        _print_node(node.right, child_prefix, False)
                    else:
                        lines.append(f"{child_prefix}\\-- <None>")

        _print_node(self.root, "", False)
        return "\n".join(lines)
