import logging
import hashlib
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import networkx as nx

from app.db.repositories.wardrobe import WardrobeRepository
from app.core.graph.builder import WardrobeGraphBuilder
from app.core.recommendation.search import OutfitSearcher
from app.schemas.outfit import RecommendationRequest, RecommendationResponse
from app.cache.redis import cache_client

logger = logging.getLogger(__name__)


class RecommendationService:

    # Class-level cached computational structures to avoid rebuilding graph on every request
    _cached_graph: Optional[nx.Graph] = None
    _cached_searcher: Optional[OutfitSearcher] = None
    _items_hash: Optional[str] = None
    _items_by_name: Dict[str, Dict[str, Any]] = {}

    def __init__(self, db: Session):
        self.db = db
        self.repo = WardrobeRepository(db)

    @classmethod
    def invalidate_in_memory_engine(cls):
        """Call when wardrobe items are mutated to force graph rebuild on next recommendation."""
        cls._cached_graph = None
        cls._cached_searcher = None
        cls._items_hash = None
        cls._items_by_name = {}

    def _ensure_engine(self):
        """Load wardrobe items from DB and build/update in-memory graph structures if needed."""
        items = self.repo.get_all()
        item_dicts = [item.to_dict() for item in items]
        
        # Fast hash of item names and update timestamps to check freshness
        current_hash = hashlib.md5(
            "".join(f"{it['id']}:{it.get('updated_at', '')}" for it in item_dicts).encode("utf-8")
        ).hexdigest()

        if RecommendationService._cached_searcher is None or RecommendationService._items_hash != current_hash:
            logger.info("Initializing/rebuilding in-memory recommendation graph with %d items", len(item_dicts))
            builder = WardrobeGraphBuilder(item_dicts)
            graph = builder.build_graph()
            searcher = OutfitSearcher(graph)

            RecommendationService._cached_graph = graph
            RecommendationService._cached_searcher = searcher
            RecommendationService._items_hash = current_hash
            RecommendationService._items_by_name = {it["item_name"]: it for it in item_dicts}

    def recommend(self, req: RecommendationRequest) -> Dict[str, Any]:
        """Produce outfit recommendation based on structured constraints and caching."""
        # 1. Normalize request for Redis cache key
        norm_key = json.dumps(req.model_dump(), sort_keys=True)
        key_hash = hashlib.md5(norm_key.encode("utf-8")).hexdigest()
        cache_key = f"rec:{key_hash}"

        cached_res = cache_client.get(cache_key)
        if cached_res is not None:
            cached_res["cached"] = True
            return cached_res

        self._ensure_engine()
        searcher = RecommendationService._cached_searcher
        items_map = RecommendationService._items_by_name

        strategy = req.strategy or "best"
        outfit_names: List[str] = []
        score: Optional[float] = None

        if strategy == "greedy":
            if not req.base_item or req.base_item not in items_map:
                # Default to first available item if not specified
                start = req.base_item if req.base_item in items_map else (next(iter(items_map)) if items_map else "")
            else:
                start = req.base_item
            outfit_names = searcher.greedy_outfit(start) if start else []
        elif strategy == "random":
            start = req.base_item if (req.base_item and req.base_item in items_map) else (next(iter(items_map)) if items_map else "")
            outfit_names = searcher.random_outfit(start) if start else []
        else:
            # Default "best" branch-and-bound search
            req_types = req.required_types
            if req_types is None:
                req_types = ["shirt", "pants", "watch"]
            best_res = searcher.best_outfit(req_types)
            if best_res and best_res.get("outfit"):
                outfit_names = list(best_res["outfit"])
                score = float(best_res["score"]) if best_res["score"] is not None else None

        # Build full outfit items
        outfit_items = [items_map[name] for name in outfit_names if name in items_map]

        res = {
            "strategy": strategy,
            "outfit": outfit_items,
            "score": score,
            "cached": False
        }

        # Cache valid recommendations in Redis
        cache_client.set(cache_key, res, ttl=3600)
        return res
