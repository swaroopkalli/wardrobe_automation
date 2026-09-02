from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, UniqueConstraint
from app.db.database import Base


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_name = Column(String(255), nullable=False, unique=True, index=True)
    type = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=True, index=True)  # extensible slot (tops, bottoms, footwear, accessories, etc.)
    layer_index = Column(Integer, nullable=False, default=0) # 0 for base, 1 for mid, 2 for outer
    color_name = Column(String(50), nullable=True)

    # Main Color Attributes
    reds = Column(Integer, nullable=False, default=0)
    green = Column(Integer, nullable=False, default=0)
    blue = Column(Integer, nullable=False, default=0)
    hue = Column(Float, nullable=False, default=0.0)

    # Watch-specific strap/dial attributes (extensible)
    strap_reds = Column(Integer, nullable=True)
    strap_green = Column(Integer, nullable=True)
    strap_blue = Column(Integer, nullable=True)
    strap_hue = Column(Float, nullable=True)

    dial_reds = Column(Integer, nullable=True)
    dial_green = Column(Integer, nullable=True)
    dial_blue = Column(Integer, nullable=True)
    dial_hue = Column(Float, nullable=True)

    # Style attributes
    formality = Column(Float, nullable=False, default=5.0)
    vibe = Column(JSON, nullable=False, default=list)  # Stored as JSON list of strings

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "item_name": self.item_name,
            "type": self.type,
            "category": self.category,
            "layer_index": self.layer_index,
            "color_name": self.color_name,
            "reds": self.reds,
            "green": self.green,
            "blue": self.blue,
            "hue": self.hue,
            "color_vec": [self.reds, self.green, self.blue],
            "strap_reds": self.strap_reds,
            "strap_green": self.strap_green,
            "strap_blue": self.strap_blue,
            "strap_hue": self.strap_hue,
            "strap_color_vec": [self.strap_reds, self.strap_green, self.strap_blue] if self.strap_reds is not None else None,
            "dial_reds": self.dial_reds,
            "dial_green": self.dial_green,
            "dial_blue": self.dial_blue,
            "dial_hue": self.dial_hue,
            "dial_color_vec": [self.dial_reds, self.dial_green, self.dial_blue] if self.dial_reds is not None else None,
            "formality": self.formality,
            "vibe": self.vibe or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
