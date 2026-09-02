from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.wardrobe import WardrobeItem
from app.schemas.wardrobe import WardrobeItemCreate, WardrobeItemUpdate


class WardrobeRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, item_type: Optional[str] = None, category: Optional[str] = None) -> List[WardrobeItem]:
        query = self.db.query(WardrobeItem)
        if item_type:
            query = query.filter(WardrobeItem.type == item_type.lower().strip())
        if category:
            query = query.filter(WardrobeItem.category == category.lower().strip())
        return query.order_by(WardrobeItem.type, WardrobeItem.item_name).all()

    def get_by_id(self, item_id: int) -> Optional[WardrobeItem]:
        return self.db.query(WardrobeItem).filter(WardrobeItem.id == item_id).first()

    def get_by_name(self, item_name: str) -> Optional[WardrobeItem]:
        return self.db.query(WardrobeItem).filter(WardrobeItem.item_name == item_name).first()

    def create(self, item_in: WardrobeItemCreate) -> WardrobeItem:
        db_item = WardrobeItem(
            item_name=item_in.item_name,
            type=item_in.type.lower().strip(),
            category=item_in.category.lower().strip() if item_in.category else None,
            color_name=item_in.color_name,
            reds=item_in.reds,
            green=item_in.green,
            blue=item_in.blue,
            hue=item_in.hue,
            strap_reds=item_in.strap_reds,
            strap_green=item_in.strap_green,
            strap_blue=item_in.strap_blue,
            strap_hue=item_in.strap_hue,
            dial_reds=item_in.dial_reds,
            dial_green=item_in.dial_green,
            dial_blue=item_in.dial_blue,
            dial_hue=item_in.dial_hue,
            formality=item_in.formality,
            vibe=item_in.vibe,
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update(self, item_id: int, item_in: WardrobeItemUpdate) -> Optional[WardrobeItem]:
        db_item = self.get_by_id(item_id)
        if not db_item:
            return None

        update_data = item_in.model_dump(exclude_unset=True)
        if "type" in update_data and update_data["type"]:
            update_data["type"] = update_data["type"].lower().strip()
        if "category" in update_data and update_data["category"]:
            update_data["category"] = update_data["category"].lower().strip()

        for key, value in update_data.items():
            setattr(db_item, key, value)

        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def delete(self, item_id: int) -> bool:
        db_item = self.get_by_id(item_id)
        if not db_item:
            return False
        self.db.delete(db_item)
        self.db.commit()
        return True
