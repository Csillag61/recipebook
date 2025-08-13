from django.shortcuts import render, get_object_or_404, redirect
from .models import Recipe, RecipeIngredient
from .forms import RecipeForm
from django.contrib.auth.decorators import login_required

def recipe_list(request):
    recipes = Recipe.objects.all().order_by('-id')
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    ingredients = recipe.ingredients.all()
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'ingredients': ingredients
    })

@login_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            form.save_m2m()
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_form.html', {'form': form})
