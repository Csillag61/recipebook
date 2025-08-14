from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.forms import inlineformset_factory
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Recipe, RecipeIngredient
from .forms import RecipeForm, RecipeIngredientInlineFormSet
from .RecipeIngredientForm import RecipeIngredientForm


# List (with search + pagination)
def recipe_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = (
        Recipe.objects.select_related("author", "category")
        .prefetch_related("tags", "recipe_ingredients__ingredient")
        .order_by("-id")
    )
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(story__icontains=q)
            | Q(instructions__icontains=q)
            | Q(tags__name__icontains=q)
        ).distinct()

    paginator = Paginator(qs, 12)  # 12 per page
    page_number = request.GET.get("page")
    recipes = paginator.get_page(page_number)

    return render(
        request,
        "recipes/recipe_list.html",
        {
            "recipes": recipes,
            "q": q,
        },
    )


# Detail
def recipe_detail(request, pk):
    recipe = get_object_or_404(
        Recipe.objects.select_related("author", "category").prefetch_related(
            "tags", "recipe_ingredients__ingredient"
        ),
        pk=pk,
    )
    return render(request, "recipes/recipe_detail.html", {"recipe": recipe})


# Create
@login_required
def recipe_create(request):
    RecipeIngredientFormSet = inlineformset_factory(
        Recipe,
        RecipeIngredient,
        form=RecipeIngredientForm,
        formset=RecipeIngredientInlineFormSet,
        fields=("ingredient", "quantity", "unit"),
        extra=10,
        can_delete=True,
        min_num=1,
        validate_min=True,
    )

    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        temp_parent = Recipe(author=request.user)
        formset = RecipeIngredientFormSet(request.POST, instance=temp_parent)

        if form.is_valid() and formset.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            form.save_m2m()  # save tags (ManyToMany)
            formset.instance = recipe
            formset.save()
            messages.success(request, "Recipe created.")
            return redirect("recipes:recipe_list")
        messages.error(request, "Please fix the errors below.")
    else:
        form = RecipeForm()
        formset = RecipeIngredientFormSet()

    return render(request, "recipes/recipe_form.html", {"form": form, "formset": formset})


# Register
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("recipes:recipe_list")
    else:
        form = UserCreationForm()
    return render(request, "recipes/register.html", {"form": form})


# Profile (with pagination)
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    qs = (
        Recipe.objects.filter(author=profile_user)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-id")
    )
    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    recipes = paginator.get_page(page_number)

    return render(
        request,
        "recipes/profile.html",
        {"profile_user": profile_user, "recipes": recipes},
    )


# Update
@login_required
def recipe_update(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe.author != request.user:
        return HttpResponseForbidden("Not allowed")

    RecipeIngredientFormSet = inlineformset_factory(
        Recipe,
        RecipeIngredient,
        form=RecipeIngredientForm,
        formset=RecipeIngredientInlineFormSet,
        fields=("ingredient", "quantity", "unit"),
        extra=5,
        can_delete=True,
        min_num=1,
        validate_min=True,
    )

    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        if form.is_valid() and formset.is_valid():
            obj = form.save(commit=False)
            if not obj.author_id:
                obj.author = request.user
            obj.save()
            form.save_m2m()  # save tags changes
            formset.instance = obj
            formset.save()
            messages.success(request, "Recipe updated.")
            return redirect("recipes:recipe_list")
        messages.error(request, "Please fix the errors below.")
    else:
        form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSet(instance=recipe)

    return render(request, "recipes/recipe_form.html", {"form": form, "formset": formset})


# Delete
@login_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe.author != request.user:
        return HttpResponseForbidden("Not allowed")
    if request.method == "POST":
        recipe.delete()
        messages.success(request, "Recipe deleted.")
        return redirect("recipes:recipe_list")
    return render(request, "recipes/recipe_confirm_delete.html", {"recipe": recipe})
