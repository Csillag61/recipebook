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
    RecipeIngredientFormSet = inlineformset_factory(
        Recipe, RecipeIngredient, fields=('ingredient', 'quantity', 'unit'), extra=15, can_delete=True
    )
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        formset = RecipeIngredientFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user  # Set the author field
            recipe.save()
            formset.instance = recipe
            formset.save()
            return redirect("recipe_detail", pk=recipe.pk)
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
