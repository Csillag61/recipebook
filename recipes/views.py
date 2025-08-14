from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from .models import Recipe, RecipeIngredient
from .forms import RecipeForm
from .RecipeIngredientForm import RecipeIngredientForm 
  # Assuming you have a form for recipe creation


def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, "recipes/recipe_list.html", {"recipes": recipes})


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, "recipes/recipe_detail.html", {"recipe": recipe})


@login_required
def recipe_create(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            form.save_m2m()  # Save ManyToMany fields like ingredients and tags
            return redirect("recipe_list")
        else:
            # Form is invalid, show errors
            formset = RecipeIngredientFormSet()
            return render(request, "recipes/recipe_form.html", {"form": form, "formset": formset})
    else:
        form = RecipeForm()
        formset = RecipeIngredientFormSet()
    return render(request, "recipes/recipe_form.html", {"form": form, "formset": formset})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("recipe_list")
    else:
        form = UserCreationForm()
    return render(request, "recipes/register.html", {"form": form})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    recipes = Recipe.objects.filter(user=profile_user)
    return render(
        request,
        "recipes/profile.html",
        {"profile_user": profile_user, "recipes": recipes},
    )

RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    extra=1,
    can_delete=True
)
