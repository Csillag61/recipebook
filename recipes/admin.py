from django.contrib import admin
from django.utils.html import format_html

from .models import Recipe, Category, Tag, Ingredient, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    fields = ("ingredient", "quantity", "unit")
    extra = 1
    autocomplete_fields = ("ingredient",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "cooking_time", "cooking_time_unit")
    list_filter = ("category", "tags")
    search_fields = ("title", "story", "description", "instructions")
    autocomplete_fields = ("author", "category")
    filter_horizontal = ("tags",)
    inlines = [RecipeIngredientInline]

    readonly_fields = ("image_preview",)
    fields = (
        "title",
        "author",
        "category",
        "story",
        "description",
        "instructions",
        ("cooking_time", "cooking_time_unit"),
        "tags",
        "image",
        "image_preview",
    )

    def image_preview(self, obj):
        if obj and getattr(obj, "image", None):
            try:
                return format_html(
                    '<img src="{}" style="max-height:120px;" />', obj.image.url
                )
            except Exception:
                return "-"
        return "-"

    image_preview.short_description = "Image preview"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)
