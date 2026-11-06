"""
Smart Campus Algorithmic Engine: Custom Graph & Dijkstra Shortest Path
File: core/graph.py

Features:
- Weighted Adjacency List graph representation.
- Custom MinHeap-driven Dijkstra's Algorithm: O((V + E) log V) time complexity.
- Turn-by-turn route generation with distances, walking times, and accessibility filters.
- Wavefront exploration tracking (visited nodes order) for visual UI animation.
"""

from typing import Dict, List, Optional, Set, Tuple
from core.min_heap import MinHeap
from core.queue import LinkedQueue
from core.stack import LinkedStack


class Landmark:
    """Represents a vertex in the campus navigation graph."""

    def __init__(
        self,
        node_id: str,
        name: str,
        x: int,
        y: int,
        category: str = "General",
        description: str = ""
    ):
        self.node_id: str = node_id
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.category: str = category
        self.description: str = description

    def to_dict(self) -> dict:
        return {
            "id": self.node_id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "category": self.category,
            "description": self.description
        }

    def __repr__(self) -> str:
        return f"Landmark({self.node_id}: '{self.name}')"


class Edge:
    """Represents a weighted pathway between two campus landmarks."""

    def __init__(
        self,
        source: str,
        dest: str,
        weight: float,
        is_accessible: bool = True,
        path_name: str = "Walkway"
    ):
        if weight <= 0:
            raise ValueError("Edge weight (distance) must be positive.")
        self.source: str = source
        self.dest: str = dest
        self.weight: float = weight
        self.is_accessible: bool = is_accessible
        self.path_name: str = path_name

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "dest": self.dest,
            "weight": self.weight,
            "is_accessible": self.is_accessible,
            "path_name": self.path_name
        }

    def __repr__(self) -> str:
        acc = " [Accessible]" if self.is_accessible else " [Stairs]"
        return f"Edge({self.source} -> {self.dest}, {self.weight}m, '{self.path_name}'{acc})"


class CampusGraph:
    """
    Campus Map Graph represented via Adjacency List.
    Employs custom Min-Heap for Dijkstra's shortest path.
    """

    def __init__(self):
        self.nodes: Dict[str, Landmark] = {}
        self.adj: Dict[str, List[Edge]] = {}

    def add_node(self, landmark: Landmark) -> None:
        self.nodes[landmark.node_id] = landmark
        if landmark.node_id not in self.adj:
            self.adj[landmark.node_id] = []

    def add_edge(
        self,
        u: str,
        v: str,
        weight: float,
        is_accessible: bool = True,
        path_name: str = "Walkway",
        bidirectional: bool = True
    ) -> None:
        if u not in self.nodes or v not in self.nodes:
            raise KeyError(f"Both nodes ({u}, {v}) must be registered before creating an edge.")

        edge_forward = Edge(u, v, weight, is_accessible, path_name)
        self.adj[u].append(edge_forward)

        if bidirectional:
            edge_backward = Edge(v, u, weight, is_accessible, path_name)
            self.adj[v].append(edge_backward)

    def get_node(self, node_id: str) -> Optional[Landmark]:
        return self.nodes.get(node_id)

    def all_nodes(self) -> List[Landmark]:
        return list(self.nodes.values())

    def all_edges(self) -> List[Edge]:
        edges = []
        for edge_list in self.adj.values():
            edges.extend(edge_list)
        return edges

    # -------------------------------------------------------------------------
    # Graph Traversals: BFS & DFS (O(V + E))
    # -------------------------------------------------------------------------

    def bfs(self, start_id: str) -> List[str]:
        """
        Breadth-First Search (BFS) using custom LinkedQueue.
        Explores vertices level-by-level in O(V + E) time.
        """
        if start_id not in self.nodes:
            return []

        visited: Set[str] = set()
        traversal_order: List[str] = []
        queue = LinkedQueue()

        queue.enqueue(start_id)
        visited.add(start_id)

        while not queue.is_empty():
            curr = queue.dequeue()
            traversal_order.append(curr)

            for edge in self.adj.get(curr, []):
                neighbor = edge.dest
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.enqueue(neighbor)

        return traversal_order

    def dfs(self, start_id: str) -> List[str]:
        """
        Depth-First Search (DFS) using custom LinkedStack.
        Explores pathways deeply before backtracking in O(V + E) time.
        """
        if start_id not in self.nodes:
            return []

        visited: Set[str] = set()
        traversal_order: List[str] = []
        stack = LinkedStack()

        stack.push(start_id)

        while not stack.is_empty():
            curr = stack.pop()
            if curr not in visited:
                visited.add(curr)
                traversal_order.append(curr)

                # Push neighbors in reverse order for deterministic exploration
                neighbors = [e.dest for e in self.adj.get(curr, [])]
                for neighbor in reversed(neighbors):
                    if neighbor not in visited:
                        stack.push(neighbor)

        return traversal_order

    # -------------------------------------------------------------------------
    # Dijkstra's Algorithm with Custom MinHeap: O((V + E) log V)
    # -------------------------------------------------------------------------

    def find_shortest_path(
        self,
        start_id: str,
        dest_id: str,
        accessible_only: bool = False
    ) -> Optional[dict]:
        """
        Calculates the shortest walking route between two campus landmarks.
        Supports filtering out stairs / non-wheelchair-accessible paths.
        Returns detailed path metrics or None if unreachable.
        """
        if start_id not in self.nodes or dest_id not in self.nodes:
            return None

        if start_id == dest_id:
            start_node = self.nodes[start_id]
            return {
                "found": True,
                "start": start_node.to_dict(),
                "destination": start_node.to_dict(),
                "total_distance_m": 0.0,
                "estimated_minutes": 0.0,
                "path_node_ids": [start_id],
                "path_landmarks": [start_node.to_dict()],
                "turn_by_turn": ["You are already at your destination."],
                "visited_order": [start_id]
            }

        # Distance table and predecessor map
        dist: Dict[str, float] = {node_id: float("inf") for node_id in self.nodes}
        parent: Dict[str, Tuple[Optional[str], Optional[Edge]]] = {node_id: (None, None) for node_id in self.nodes}
        visited: Set[str] = set()
        visited_order: List[str] = []

        dist[start_id] = 0.0
        pq = MinHeap()
        pq.insert(start_id, 0.0)

        found = False

        while not pq.is_empty():
            min_item = pq.extract_min()
            u = min_item.item_id
            current_dist = min_item.priority

            if u in visited:
                continue

            visited.add(u)
            visited_order.append(u)

            # Early termination when destination reached
            if u == dest_id:
                found = True
                break

            # If current distance exceeds known distance, skip
            if current_dist > dist[u]:
                continue

            # Relax adjacent edges
            for edge in self.adj.get(u, []):
                v = edge.dest

                # Skip if accessibility requirement is violated
                if accessible_only and not edge.is_accessible:
                    continue

                if v in visited:
                    continue

                new_dist = dist[u] + edge.weight
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    parent[v] = (u, edge)
                    pq.insert(v, new_dist)

        if not found or dist[dest_id] == float("inf"):
            return None

        # Reconstruct path from destination backwards
        path_ids: List[str] = []
        path_edges: List[Edge] = []
        curr = dest_id

        while curr is not None:
            path_ids.append(curr)
            prev_node, used_edge = parent[curr]
            if used_edge is not None:
                path_edges.append(used_edge)
            curr = prev_node

        path_ids.reverse()
        path_edges.reverse()

        # Build turn-by-turn directions
        turn_by_turn: List[str] = []
        for i, edge in enumerate(path_edges):
            u_name = self.nodes[edge.source].name
            v_name = self.nodes[edge.dest].name
            acc_tag = "" if edge.is_accessible else " (Warning: Contains stairs)"
            step_desc = f"Step {i+1}: Walk {edge.weight:.0f}m along '{edge.path_name}' from {u_name} to {v_name}{acc_tag}."
            turn_by_turn.append(step_desc)

        total_meters = dist[dest_id]
        # Average campus walking speed: 80 meters/minute (~4.8 km/h)
        est_minutes = round(total_meters / 80.0, 1)

        return {
            "found": True,
            "start": self.nodes[start_id].to_dict(),
            "destination": self.nodes[dest_id].to_dict(),
            "total_distance_m": round(total_meters, 1),
            "estimated_minutes": est_minutes,
            "path_node_ids": path_ids,
            "path_landmarks": [self.nodes[nid].to_dict() for nid in path_ids],
            "turn_by_turn": turn_by_turn,
            "visited_order": visited_order
        }
