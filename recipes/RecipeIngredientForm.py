from typing import cast

from django import forms
from django.forms import ModelChoiceField, ChoiceField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div

from .models import RecipeIngredient


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "quantity", "unit"]
        labels = {
            "ingredient": "Ingredient",
            "quantity": "Quantity",
            "unit": "Unit",
        }
        widgets = {
            # Select2 is initialized globally in base.html
            "ingredient": forms.Select(
                attrs={"class": "form-control select2", "data-placeholder": "— Select ingredient —"}
            ),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "any", "min": 0}),
            # Unit widget may be overridden in __init__ if not a ChoiceField
            "unit": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Better empty label for ingredient (if FK)
        if "ingredient" in self.fields and isinstance(self.fields["ingredient"], ModelChoiceField):
            ing_field = cast(ModelChoiceField, self.fields["ingredient"])
            ing_field.empty_label = "— Select ingredient —"

        # If unit is NOT a ChoiceField (no choices on the model), use a TextInput instead
        if "unit" in self.fields and not isinstance(self.fields["unit"], ChoiceField):
            self.fields["unit"].widget = forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. g, ml, tsp"}
            )

        # Crispy-Forms helper (outer <form> lives in the template)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div("ingredient", css_class="col-md-6"),
                Div("quantity", css_class="col-md-3"),
                Div("unit", css_class="col-md-3"),
                css_class="row",
            )
        )

    def clean_quantity(self):
        value = self.cleaned_data.get("quantity")
        if value in (None, ""):
            return 0
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise forms.ValidationError("Enter a valid number.")
        if value < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return value

    def clean_unit(self):
        unit = self.cleaned_data.get("unit")
        if unit is None:
            return unit
        # Normalize basic whitespace/casing for free-text units
        if not isinstance(self.fields.get("unit"), ChoiceField):
            return str(unit).strip()
        return unit
