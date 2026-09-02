import itertools
import random
from typing import List, Dict, Any, Optional, Tuple, Sequence
import networkx as nx


class OutfitSearcher:

    def __init__(self, graph: nx.Graph):
        self.G = graph
        self._edge_weights: Dict[Tuple[str, str], float] = {}
        for u, v, d in self.G.edges(data=True):
            w = d.get("weight", 0.0)
            self._edge_weights[(u, v)] = w
            self._edge_weights[(v, u)] = w

    def greedy_outfit(self, start_item: str) -> List[str]:
        if start_item not in self.G:
            return []

        start_type = self.G.nodes[start_item]["type"]
        outfit = [start_item]
        used_types = {start_type}

        neighbors = sorted(
            self.G[start_item].items(),
            key=lambda x: x[1]["weight"],
            reverse=True
        )

        for node, data in neighbors:
            node_type = self.G.nodes[node]["type"]
            if node_type not in used_types:
                outfit.append(node)
                used_types.add(node_type)

        return outfit

    def best_outfit(self, required_types: Optional[Sequence[str]] = None) -> Dict[str, Any]:
        """
        Exact Branch-and-Bound search for globally optimal outfit across required item types.
        """
        if required_types is None:
            required_types = ["shirt", "pants", "shoes", "watch"]

        nodes_by_type = {
            t: [
                n for n, d in self.G.nodes(data=True)
                if d["type"] == t
            ]
            for t in required_types
        }

        # If any requested type is missing from the graph, return no outfit
        if any(len(items) == 0 for items in nodes_by_type.values()):
            return {
                "outfit": None,
                "score": -1
            }

        ordered_types = list(required_types)
        num_types = len(ordered_types)

        candidates_by_level = []
        for t in ordered_types:
            cands = nodes_by_type[t]
            cands_sorted = sorted(
                cands,
                key=lambda item: sum(self._edge_weights.get((item, nbr), 0.0) for nbr in self.G[item]),
                reverse=True
            )
            candidates_by_level.append(cands_sorted)

        max_edge_between_types = {}
        for i in range(num_types):
            for j in range(i + 1, num_types):
                max_w = 0.0
                for item1 in candidates_by_level[i]:
                    for item2 in candidates_by_level[j]:
                        w = self._edge_weights.get((item1, item2), 0.0)
                        if w > max_w:
                            max_w = w
                max_edge_between_types[(i, j)] = max_w

        best_combo: Optional[Tuple[str, ...]] = None
        best_score = -1.0

        def branch_and_bound(level: int, current_outfit: List[str], current_score: float):
            nonlocal best_combo, best_score

            if level == num_types:
                if current_score > best_score:
                    best_score = current_score
                    best_combo = tuple(current_outfit)
                return

            upper_bound = current_score
            for unassigned_level in range(level, num_types):
                for assigned_level in range(level):
                    upper_bound += max_edge_between_types.get((assigned_level, unassigned_level), 1.0)

            for i in range(level, num_types):
                for j in range(i + 1, num_types):
                    upper_bound += max_edge_between_types.get((i, j), 1.0)

            if upper_bound <= best_score:
                return

            for candidate in candidates_by_level[level]:
                added_score = 0.0
                for chosen in current_outfit:
                    added_score += self._edge_weights.get((candidate, chosen), 0.0)

                current_outfit.append(candidate)
                branch_and_bound(level + 1, current_outfit, current_score + added_score)
                current_outfit.pop()

        branch_and_bound(0, [], 0.0)

        return {
            "outfit": best_combo,
            "score": best_score
        }

    def random_outfit(self, start_item: str, steps: int = 3) -> List[str]:
        if start_item not in self.G:
            return []

        current = start_item
        outfit = [current]

        for _ in range(steps):
            neighbors = list(self.G.neighbors(current))
            if not neighbors:
                break
            current = random.choice(neighbors)
            if current not in outfit:
                outfit.append(current)

        return outfit
