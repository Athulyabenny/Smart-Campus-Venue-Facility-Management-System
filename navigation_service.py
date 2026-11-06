"""
Smart Campus Algorithmic Engine: Campus Navigation Service
File: services/navigation_service.py

High-level navigation service leveraging custom Graph Adjacency List and Min-Heap Dijkstra.
"""

import json
import os
from typing import Dict, List, Optional
from core.graph import CampusGraph, Landmark, Edge


class NavigationService:
    """
    Campus Navigation Service managing landmark graphs and Dijkstra route generation.
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.graph = CampusGraph()
        if data_dir:
            self._load_landmarks(data_dir)

    def _load_landmarks(self, data_dir: str) -> None:
        path = os.path.join(data_dir, "campus_landmarks.json")
        if not os.path.exists(path):
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for lm in data.get("landmarks", []):
            landmark = Landmark(
                node_id=lm["id"],
                name=lm["name"],
                x=lm["x"],
                y=lm["y"],
                category=lm.get("category", "General"),
                description=lm.get("description", "")
            )
            self.graph.add_node(landmark)

        for pw in data.get("pathways", []):
            self.graph.add_edge(
                u=pw["source"],
                v=pw["dest"],
                weight=float(pw["weight"]),
                is_accessible=pw.get("is_accessible", True),
                path_name=pw.get("path_name", "Walkway"),
                bidirectional=True
            )

    def get_all_landmarks(self) -> List[dict]:
        return [lm.to_dict() for lm in self.graph.all_nodes()]

    def get_landmark(self, node_id: str) -> Optional[dict]:
        lm = self.graph.get_node(node_id)
        return lm.to_dict() if lm else None

    def get_all_pathways(self) -> List[dict]:
        return [edge.to_dict() for edge in self.graph.all_edges()]

    def find_route(
        self,
        start_id: str,
        dest_id: str,
        accessible_only: bool = False
    ) -> Optional[dict]:
        """
        Executes Dijkstra's algorithm to find the optimal path.
        """
        return self.graph.find_shortest_path(start_id, dest_id, accessible_only=accessible_only)
