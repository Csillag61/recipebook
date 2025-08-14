from django import forms

from .models import Recipe, RecipeIngredient

class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "quantity", "unit"]
        widgets = {
            "ingredient": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "unit": forms.Select(attrs={"class": "form-control"}),
        }
