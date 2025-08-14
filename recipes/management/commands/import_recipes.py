from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from decimal import Decimal
import json

from recipes.models import Recipe, Category, Tag, Ingredient, RecipeIngredient

# --- New: Hungarian → English mappings ---
KEYS_HU_TO_EN = {
    # recipe fields
    "cím": "title",
    "title": "title",
    "történet": "story",
    "leírás": "description",
    "utasítások": "instructions",
    "elkészítési_idő": "cooking_time",
    "főzési_idő": "cooking_time",
    "elkészítési_idő_egység": "cooking_time_unit",
    "főzési_idő_egység": "cooking_time_unit",
    "kategória": "category",
    "címkék": "tags",
    "hozzávalók": "ingredients",

    # ingredient item fields
    "összetevő": "ingredient",
    "alapanyag": "ingredient",
    "hozzávaló": "ingredient",
    "mennyiség": "quantity",
    "egység": "unit",

    # top-level
    "receptek": "recipes",
}

UNITS_HU_TO_EN = {
    "perc": "min",
    "percek": "min",
    "p": "min",
    "óra": "hr",
    "órák": "hr",
    "h": "hr",
}

def translate_key(k: str) -> str:
    return KEYS_HU_TO_EN.get(k, k)

def normalize_unit(u: str) -> str:
    if not u:
        return ""
    u_norm = u.strip().lower()
    return UNITS_HU_TO_EN.get(u_norm, u.strip())

def normalize_recipe_item(item: dict) -> dict:
    """Return a new dict with English keys and normalized ingredient entries."""
    out = {}
    # First pass: translate top-level keys
    for k, v in item.items():
        out_key = translate_key(k)
        out[out_key] = v

    # Normalize ingredients list (translate keys inside each ingredient)
    ingredients = out.get("ingredients") or []
    norm_ingredients = []
    for ing in ingredients:
        if not isinstance(ing, dict):
            continue
        ing_norm = {}
        for k, v in ing.items():
            k_en = translate_key(k)
            ing_norm[k_en] = v
        # Normalize unit text
        ing_norm["unit"] = normalize_unit(str(ing_norm.get("unit", "")))
        norm_ingredients.append(ing_norm)
    out["ingredients"] = norm_ingredients

    # Normalize cooking_time_unit if present
    if "cooking_time_unit" in out:
        out["cooking_time_unit"] = normalize_unit(str(out["cooking_time_unit"]))

    return out
# --- end new ---

User = get_user_model()

class Command(BaseCommand):
    help = "Import recipes from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument("json_path", type=str, help="Path to JSON file")
        parser.add_argument("--username", type=str, required=True, help="Author username to assign")
        parser.add_argument("--update", action="store_true", help="Update if recipe with same title exists")

    def handle(self, *args, **options):
        path = options["json_path"]
        username = options["username"]
        do_update = options["update"]

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise CommandError(f"Cannot read JSON: {e}")

        # Accept list or dict with "recipes" or Hungarian "receptek"
        if isinstance(data, list):
            raw_items = data
        elif isinstance(data, dict):
            raw_items = data.get("recipes") or data.get("receptek")
            if raw_items is None:
                raise CommandError("JSON must be a list or an object with 'recipes' or 'receptek'.")
        else:
            raise CommandError("Unsupported JSON structure.")

        # Normalize each recipe item (keys and units)
        items = [normalize_recipe_item(it) for it in raw_items]

        try:
            author = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' not found")

        created = updated = 0

        for item in items:
            title = item.get("title")
            if not title:
                self.stderr.write("Skipping item without title")
                continue

            defaults = {
                "story": item.get("story", ""),
                "description": item.get("description", ""),
                "instructions": item.get("instructions", ""),
                "cooking_time": item.get("cooking_time", 0) or 0,
                "cooking_time_unit": item.get("cooking_time_unit", "min"),
                "author": author,
                "category": None,
            }

            cat_name = item.get("category")
            if cat_name:
                defaults["category"], _ = Category.objects.get_or_create(name=cat_name)

            recipe, was_created = Recipe.objects.get_or_create(title=title, defaults=defaults)
            if not was_created and do_update:
                for k, v in defaults.items():
                    setattr(recipe, k, v)
                recipe.save()
                updated += 1
            elif was_created:
                created += 1

            # Tags
            tag_objs = []
            for t in (item.get("tags") or []):
                tag, _ = Tag.objects.get_or_create(name=t)
                tag_objs.append(tag)
            if do_update:
                recipe.tags.set(tag_objs)  # clears if empty; sets if provided
            elif tag_objs:
                recipe.tags.set(tag_objs)

            # Ingredients
            if do_update:
                RecipeIngredient.objects.filter(recipe=recipe).delete()

            for ing in (item.get("ingredients") or []):
                name = ing.get("ingredient") or ing.get("name")
                if not name:
                    continue
                ingredient_obj, _ = Ingredient.objects.get_or_create(name=name)

                try:
                    qty = Decimal(str(ing.get("quantity", "0")))
                except Exception:
                    qty = Decimal("0")

                unit = (ing.get("unit") or "").strip()
                RecipeIngredient.objects.create(
                    recipe=recipe, ingredient=ingredient_obj, quantity=qty, unit=unit
                )

        self.stdout.write(self.style.SUCCESS(f"Imported. Created: {created}, Updated: {updated}"))
