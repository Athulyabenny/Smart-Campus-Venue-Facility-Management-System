"""
Smart Campus Algorithmic Engine: Phase 2 Hierarchical Structures
File: core/bst.py

Custom Binary Search Tree (BST) for student and academic record indexing.
Implements pointer-based node architecture with full traversal suites:
- Inorder Traversal   (Left, Root, Right) -> Yields ascending sorted order
- Preorder Traversal  (Root, Left, Right) -> Used for tree cloning and serialization
- Postorder Traversal (Left, Right, Root) -> Used for bottom-up node deallocation

Time Complexities:
    * Search:     O(log n) average, O(n) worst-case
    * Insert:     O(log n) average, O(n) worst-case
    * Delete:     O(log n) average, O(n) worst-case
    * Traversals: O(n)
"""

from typing import Any, Callable, List, Optional, Tuple


class BSTNode:
    """Node in a Binary Search Tree."""

    def __init__(self, key: Any, data: Any = None):
        self.key: Any = key
        self.data: Any = data if data is not None else key
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None

    def __repr__(self) -> str:
        return f"BSTNode(key={self.key}, data={self.data})"


class BinarySearchTree:
    """
    Textbook-grade Binary Search Tree implementation.
    Zero external libraries used.
    """

    def __init__(self):
        self.root: Optional[BSTNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.root is None

    # -------------------------------------------------------------------------
    # Insertion
    # -------------------------------------------------------------------------

    def insert(self, key: Any, data: Any = None) -> None:
        """Inserts a key-data pair into the BST."""
        self.root = self._insert_recursive(self.root, key, data)

    def _insert_recursive(self, node: Optional[BSTNode], key: Any, data: Any) -> BSTNode:
        if node is None:
            self._size += 1
            return BSTNode(key, data)

        if key < node.key:
            node.left = self._insert_recursive(node.left, key, data)
        elif key > node.key:
            node.right = self._insert_recursive(node.right, key, data)
        else:
            # Key already exists: update data in-place
            node.data = data if data is not None else key

        return node

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------

    def search(self, key: Any) -> Optional[Any]:
        """Searches for key and returns associated data, or None if not found."""
        current = self.root
        while current is not None:
            if key == current.key:
                return current.data
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return None

    def contains(self, key: Any) -> bool:
        return self.search(key) is not None

    # -------------------------------------------------------------------------
    # Deletion
    # -------------------------------------------------------------------------

    def delete(self, key: Any) -> bool:
        """Deletes a node with the given key. Returns True if deleted, False otherwise."""
        initial_size = self._size
        self.root = self._delete_recursive(self.root, key)
        return self._size < initial_size

    def _get_min_node(self, node: BSTNode) -> BSTNode:
        curr = node
        while curr.left is not None:
            curr = curr.left
        return curr

    def _delete_recursive(self, node: Optional[BSTNode], key: Any) -> Optional[BSTNode]:
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete_recursive(node.left, key)
        elif key > node.key:
            node.right = self._delete_recursive(node.right, key)
        else:
            # Match found
            self._size -= 1
            # Case 1: Leaf node or 1 child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Case 2: Two children -> find inorder successor (min in right subtree)
            successor = self._get_min_node(node.right)
            node.key = successor.key
            node.data = successor.data

            # Delete the successor from right subtree
            self._size += 1  # Increment back since recursive call will decrement
            node.right = self._delete_recursive(node.right, successor.key)

        return node

    # -------------------------------------------------------------------------
    # Tree Traversals (Inorder, Preorder, Postorder)
    # -------------------------------------------------------------------------

    def inorder(self) -> List[Tuple[Any, Any]]:
        """
        Inorder Traversal: Left -> Root -> Right.
        Yields keys in strictly ascending sorted order.
        """
        result: List[Tuple[Any, Any]] = []

        def _traverse(node: Optional[BSTNode]):
            if node is not None:
                _traverse(node.left)
                result.append((node.key, node.data))
                _traverse(node.right)

        _traverse(self.root)
        return result

    def preorder(self) -> List[Tuple[Any, Any]]:
        """
        Preorder Traversal: Root -> Left -> Right.
        Useful for cloning or serializing tree structure.
        """
        result: List[Tuple[Any, Any]] = []

        def _traverse(node: Optional[BSTNode]):
            if node is not None:
                result.append((node.key, node.data))
                _traverse(node.left)
                _traverse(node.right)

        _traverse(self.root)
        return result

    def postorder(self) -> List[Tuple[Any, Any]]:
        """
        Postorder Traversal: Left -> Right -> Root.
        Useful for bottom-up calculation and tree deallocation.
        """
        result: List[Tuple[Any, Any]] = []

        def _traverse(node: Optional[BSTNode]):
            if node is not None:
                _traverse(node.left)
                _traverse(node.right)
                result.append((node.key, node.data))

        _traverse(self.root)
        return result

    # -------------------------------------------------------------------------
    # Auxiliary Metrics & Visualizer
    # -------------------------------------------------------------------------

    def height(self) -> int:
        """Calculates maximum depth/height of the tree."""
        def _height(node: Optional[BSTNode]) -> int:
            if node is None:
                return 0
            return 1 + max(_height(node.left), _height(node.right))
        return _height(self.root)

    def print_ascii_tree(self) -> str:
        """Visualizes the BST in ASCII tree format for viva demonstrations."""
        if not self.root:
            return "<Empty Binary Search Tree>"

        lines: List[str] = []

        def _print_node(node: Optional[BSTNode], prefix: str = "", is_left: bool = True):
            if node is not None:
                lines.append(f"{prefix}{'|-- ' if is_left else '\\-- '}[Key: {node.key}] ({getattr(node.data, 'name', str(node.data))})")
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
