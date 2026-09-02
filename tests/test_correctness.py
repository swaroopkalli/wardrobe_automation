import unittest
import math
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


from core.data_loader import WardrobeDataLoader
from core.color_theory import color_theory_score, complementary, analogous, triadic
from core.vibe_similarity import vibe_similarity
from core.scoring import compatibility_score, color_similarity, formality_score, _watch_representative_vec, _watch_hue
from core.graph_builder import WardrobeGraphBuilder
from core.outfit_search import OutfitSearcher


class TestWardrobeCorrectness(unittest.TestCase):

    def setUp(self):
        self.loader = WardrobeDataLoader()
        self.df = self.loader.load()
        self.items = self.df.to_dict("records")
        self.builder = WardrobeGraphBuilder(self.df)
        self.G = self.builder.build_graph()
        self.searcher = OutfitSearcher(self.G)

    def test_formality_score(self):
        self.assertEqual(formality_score(5, 5), 1.0)
        self.assertEqual(formality_score(5, 4), 0.7)
        self.assertEqual(formality_score(5, 3), 0.4)
        self.assertEqual(formality_score(5, 2), 0.1)
        self.assertEqual(formality_score(5, 9), 0.1)

    def test_color_theory_rules(self):
        # Complementary (diff 180 +/- 25)
        self.assertTrue(complementary(0, 180))
        self.assertTrue(complementary(0, 160))
        self.assertFalse(complementary(0, 150))
        self.assertEqual(color_theory_score(0, 180), 1.0)

        # Analogous (diff <= 30)
        self.assertTrue(analogous(0, 25))
        self.assertTrue(analogous(350, 10))
        self.assertEqual(color_theory_score(0, 25), 0.8)

        # Triadic (diff 120 +/- 25)
        self.assertTrue(triadic(0, 120))
        self.assertTrue(triadic(0, 140))
        self.assertEqual(color_theory_score(0, 120), 0.7)

        # Default
        self.assertEqual(color_theory_score(0, 60), 0.3)

    def test_vibe_similarity(self):
        self.assertEqual(vibe_similarity([], []), 0)
        self.assertEqual(vibe_similarity(["clean"], []), 0)
        self.assertEqual(vibe_similarity(["clean", "minimal"], ["clean", "minimal"]), 1.0)
        self.assertEqual(vibe_similarity(["clean", "minimal"], ["clean", "rich"]), 1 / 3)
        self.assertEqual(vibe_similarity(["bold"], ["soft"]), 0.0)

    def test_compatibility_scoring_semantics(self):
        """Verify that compatibility scores adhere exactly to weights and formula."""
        for item1 in self.items:
            for item2 in self.items:
                if item1["type"] == item2["type"]:
                    continue
                score = compatibility_score(item1, item2)
                self.assertIsInstance(score, float)
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

                # Undirected symmetry
                rev_score = compatibility_score(item2, item1)
                self.assertEqual(score, rev_score)

    def test_graph_properties(self):
        """Verify graph nodes, edge threshold (>0.35), and cross-type constraint."""
        self.assertEqual(self.G.number_of_nodes(), len(self.items))
        for u, v, data in self.G.edges(data=True):
            self.assertGreater(data["weight"], 0.35)
            self.assertNotEqual(self.G.nodes[u]["type"], self.G.nodes[v]["type"])

    def test_best_outfit_exactness(self):
        """Test best outfit search returns valid combination with highest score."""
        types = ["shirt", "pants", "watch"]
        res = self.searcher.best_outfit(types)
        self.assertIsNotNone(res["outfit"])
        self.assertEqual(len(res["outfit"]), 3)
        self.assertAlmostEqual(res["score"], 2.10, places=2)

        # Confirm all items in outfit belong to required types
        outfit_types = [self.G.nodes[item]["type"] for item in res["outfit"]]
        self.assertEqual(sorted(outfit_types), sorted(types))


if __name__ == "__main__":
    unittest.main()
