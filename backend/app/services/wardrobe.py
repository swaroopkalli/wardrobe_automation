import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.repositories.wardrobe import WardrobeRepository
from app.schemas.wardrobe import WardrobeItemCreate, WardrobeItemUpdate
from app.models.wardrobe import WardrobeItem
from app.cache.redis import cache_client

logger = logging.getLogger(__name__)


class WardrobeService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = WardrobeRepository(db)

    def get_items(self, item_type: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        cache_key = f"wardrobe:items:type={item_type or 'all'}:cat={category or 'all'}"
        cached = cache_client.get(cache_key)
        if cached is not None:
            return cached

        items = self.repo.get_all(item_type=item_type, category=category)
        res = [item.to_dict() for item in items]
        cache_client.set(cache_key, res, ttl=1800)
        return res

    def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        cache_key = f"wardrobe:item:{item_id}"
        cached = cache_client.get(cache_key)
        if cached is not None:
            return cached

        item = self.repo.get_by_id(item_id)
        if not item:
            return None
        res = item.to_dict()
        cache_client.set(cache_key, res, ttl=3600)
        return res

    def create_item(self, item_in: WardrobeItemCreate) -> Dict[str, Any]:
        item = self.repo.create(item_in)
        self._invalidate_caches()
        return item.to_dict()

    def update_item(self, item_id: int, item_in: WardrobeItemUpdate) -> Optional[Dict[str, Any]]:
        item = self.repo.update(item_id, item_in)
        if item:
            self._invalidate_caches(item_id)
            return item.to_dict()
        return None

    def delete_item(self, item_id: int) -> bool:
        success = self.repo.delete(item_id)
        if success:
            self._invalidate_caches(item_id)
        return success

    def _invalidate_caches(self, item_id: Optional[int] = None):
        """Invalidate affected wardrobe item lists, item records, and recommendations."""
        cache_client.delete_prefix("wardrobe:items:")
        if item_id:
            cache_client.delete(f"wardrobe:item:{item_id}")
        cache_client.delete_prefix("rec:")
        cache_client.delete_prefix("compat:")
