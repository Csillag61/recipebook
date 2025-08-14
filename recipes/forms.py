from typing import cast

from django import forms
from django.forms import ModelChoiceField, BaseInlineFormSet

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div

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
        labels = {
            "cooking_time": "Cooking time",
            "cooking_time_unit": "Unit",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Enter recipe title", "class": "form-control"}
            ),
            "story": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                    "placeholder": "Short story (optional)",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    "placeholder": "Short description of the recipe",
                }
            ),
            "instructions": forms.Textarea(
                attrs={
                    "rows": 6,
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
            "cooking_time": forms.NumberInput(
                attrs={"min": 0, "class": "form-control"}
            ),
            "cooking_time_unit": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "category" in self.fields and isinstance(
            self.fields["category"], ModelChoiceField
        ):
            cat_field = cast(ModelChoiceField, self.fields["category"])
            cat_field.empty_label = "— Select category —"

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "title",
            "story",
            "description",
            Div(
                Div("cooking_time", css_class="col-md-6"),
                Div("cooking_time_unit", css_class="col-md-6"),
                css_class="row",
            ),
            "instructions",
            "image",
            Div(
                Div("category", css_class="col-md-6"),
                Div("tags", css_class="col-md-6"),
                css_class="row",
            ),
        )

    def clean_cooking_time(self):
        value = self.cleaned_data.get("cooking_time")
        if value in (None, ""):
            return 0
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise forms.ValidationError("Please enter a valid number.")
        if value < 0:
            raise forms.ValidationError("Cooking time cannot be negative.")
        return value


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ("ingredient", "quantity", "unit")
        widgets = {
            "ingredient": forms.Select(
                attrs={
                    "class": "form-control select2",
                    "data-placeholder": "— Select ingredient —",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={"step": "any", "min": 0, "class": "form-control"}
            ),
            "unit": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. g, ml, tsp"}
            ),
        }


class RecipeIngredientInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_one = False
        for form in self.forms:
            if not getattr(form, "cleaned_data", None):
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            ingredient = form.cleaned_data.get("ingredient")
            quantity = form.cleaned_data.get("quantity")
            if ingredient and quantity not in (None, ""):
                has_one = True
                break
        if not has_one:
            raise forms.ValidationError("Add at least one ingredient.")
