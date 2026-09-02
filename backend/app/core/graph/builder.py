from collections import defaultdict
from itertools import combinations
import networkx as nx
import math
from typing import Dict, Any, List, Union

from app.core.scoring import compatibility_score, watch_representative_vec, watch_hue


def preprocess_item_attributes(item: Dict[str, Any]) -> Dict[str, Any]:
    """Precompute static attributes on an item dictionary to eliminate repeated parsing."""
    if "_preprocessed" in item:
        return item

    # Representative 3D vector and its Euclidean norm
    vec = watch_representative_vec(item) if item.get("type") == "watch" else item.get("color_vec", [0, 0, 0])
    item["_rep_vec"] = vec
    item["_rep_norm"] = math.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2) if vec else 0.0

    # Representative hue
    item["_rep_hue"] = watch_hue(item)

    # Precomputed frozenset for Jaccard vibe overlap
    raw_vibe = item.get("vibe") or []
    if isinstance(raw_vibe, (list, tuple, set)):
        item["_vibe_set"] = frozenset(raw_vibe)
    else:
        item["_vibe_set"] = frozenset()

    # Precomputed formality
    form = item.get("formality")
    item["_formality"] = float(form) if form is not None and not (isinstance(form, float) and math.isnan(form)) else 0.0

    item["_preprocessed"] = True
    return item


class WardrobeGraphBuilder:

    def __init__(self, items: List[Dict[str, Any]]):
        self.items = [preprocess_item_attributes(dict(r)) for r in items]
        self.graph = nx.Graph()

    def build_graph(self) -> nx.Graph:
        self._add_nodes()
        self._add_edges()
        return self.graph

    def _add_nodes(self):
        for item in self.items:
            identifier = item.get("item_name") or str(item.get("id"))
            self.graph.add_node(
                identifier,
                type=item["type"],
                data=item
            )

    def _add_edges(self):
        items_by_type: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for item in self.items:
            items_by_type[item["type"]].append(item)

        types = list(items_by_type.keys())

        for t1, t2 in combinations(types, 2):
            for item1 in items_by_type[t1]:
                for item2 in items_by_type[t2]:
                    score = compatibility_score(item1, item2)
                    if score > 0.35:
                        id1 = item1.get("item_name") or str(item1.get("id"))
                        id2 = item2.get("item_name") or str(item2.get("id"))
                        self.graph.add_edge(
                            id1,
                            id2,
                            weight=score
                        )

    def get_graph(self) -> nx.Graph:
        return self.graph
