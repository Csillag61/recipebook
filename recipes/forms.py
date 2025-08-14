from django import forms
from .models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "title",
            "story",
            "description",
            "cooking_time",
            "cooking_time_unit",
            "instructions",
            "image",
            "category",
            "tags",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Enter recipe title",
                    "required": True,
                    "class": "form-control",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "required": True,
                    "class": "form-control",
                    "placeholder": "Short description of the recipe",
                }
            ),
            "instructions": forms.Textarea(
                attrs={
                    "rows": 5,
                    "required": True,
                    "class": "form-control",
                    "placeholder": "Step-by-step instructions",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control-file", "accept": "image/*"}
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "tags": forms.SelectMultiple(
                attrs={
                    "class": "form-control select2",
                    "data-placeholder": "Select or type tags",
                }
            ),
            "cooking_time_unit": forms.Select(attrs={"class": "form-control"}),
        }
