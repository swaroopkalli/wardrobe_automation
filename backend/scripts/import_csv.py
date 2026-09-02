import sys
import os
import ast
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import SessionLocal, engine, Base
from app.models.wardrobe import WardrobeItem


def parse_vibes(x):
    if not isinstance(x, str):
        return []
    try:
        res = ast.literal_eval(x)
        if isinstance(res, list):
            return res
        return [str(res)]
    except Exception:
        clean = x.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
        return [v.strip() for v in clean.split() if v.strip()]


def clean_val(val, default=None, is_int=False, is_float=False):
    if pd.isna(val) or val == "" or str(val).strip() == "":
        return default
    try:
        if is_int:
            return int(float(val))
        if is_float:
            return float(val)
        return val
    except (ValueError, TypeError):
        return default


def import_csv_to_postgres(csv_path: str = "data/wadrobe.csv"):
    """
    Idempotent CSV importer to populate PostgreSQL database with wardrobe items.
    """
    csv_file = Path(csv_path)
    if not csv_file.exists():
        # Check parent data directory
        csv_file = Path(__file__).parent.parent.parent / "data" / "wadrobe.csv"

    if not csv_file.exists():
        print(f"[ERROR] CSV file not found at: {csv_path}")
        return 0

    print(f"[*] Reading wardrobe CSV from: {csv_file}")
    df = pd.read_csv(csv_file, quotechar='"', skipinitialspace=True)
    print(f"[*] Loaded {len(df)} rows from CSV.")

    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    imported_count = 0
    updated_count = 0

    try:
        for idx, row in df.iterrows():
            item_name = str(row["item_name"]).strip()
            item_type = str(row["type"]).lower().strip()
            color_name = clean_val(row.get("color_name"))

            reds = clean_val(row.get("reds"), default=0, is_int=True)
            green = clean_val(row.get("green"), default=0, is_int=True)
            blue = clean_val(row.get("blue"), default=0, is_int=True)
            hue = clean_val(row.get("hue"), default=0.0, is_float=True)

            strap_reds = clean_val(row.get("strap_reds"), is_int=True)
            strap_green = clean_val(row.get("strap_green"), is_int=True)
            strap_blue = clean_val(row.get("strap_blue"), is_int=True)
            strap_hue = clean_val(row.get("strap_hue"), is_float=True)

            dial_reds = clean_val(row.get("dial_reds"), is_int=True)
            dial_green = clean_val(row.get("dial_green"), is_int=True)
            dial_blue = clean_val(row.get("dial_blue"), is_int=True)
            dial_hue = clean_val(row.get("dial_hue"), is_float=True)

            formality = clean_val(row.get("formality"), default=5.0, is_float=True)
            vibe_raw = row.get("vibe")
            vibe_list = parse_vibes(vibe_raw)

            # Assign category slot
            category = "tops" if item_type in ["shirt", "polo", "tshirt", "jacket", "hoodie"] else (
                "bottoms" if item_type in ["pants", "jeans", "shorts", "trousers"] else (
                    "accessories" if item_type in ["watch", "belt", "hat"] else (
                        "footwear" if item_type in ["shoes", "sneakers", "boots"] else item_type
                    )
                )
            )

            # Check if item already exists by unique item_name
            existing = db.query(WardrobeItem).filter(WardrobeItem.item_name == item_name).first()
            if existing:
                existing.type = item_type
                existing.category = category
                existing.color_name = color_name
                existing.reds = reds
                existing.green = green
                existing.blue = blue
                existing.hue = hue
                existing.strap_reds = strap_reds
                existing.strap_green = strap_green
                existing.strap_blue = strap_blue
                existing.strap_hue = strap_hue
                existing.dial_reds = dial_reds
                existing.dial_green = dial_green
                existing.dial_blue = dial_blue
                existing.dial_hue = dial_hue
                existing.formality = formality
                existing.vibe = vibe_list
                updated_count += 1
            else:
                new_item = WardrobeItem(
                    item_name=item_name,
                    type=item_type,
                    category=category,
                    color_name=color_name,
                    reds=reds,
                    green=green,
                    blue=blue,
                    hue=hue,
                    strap_reds=strap_reds,
                    strap_green=strap_green,
                    strap_blue=strap_blue,
                    strap_hue=strap_hue,
                    dial_reds=dial_reds,
                    dial_green=dial_green,
                    dial_blue=dial_blue,
                    dial_hue=dial_hue,
                    formality=formality,
                    vibe=vibe_list,
                )
                db.add(new_item)
                imported_count += 1

        db.commit()
        print(f"[SUCCESS] CSV Migration complete. {imported_count} new items inserted, {updated_count} existing items updated.")
        return imported_count + updated_count

    except Exception as e:
        db.rollback()
        print(f"[ERROR] CSV migration failed: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    import_csv_to_postgres()
