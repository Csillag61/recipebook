from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    title = models.CharField(max_length=100)
    story = models.TextField(help_text="Background or personal story behind the recipe")
    cooking_time = models.PositiveIntegerField(help_text="Time in minutes")
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)

    instructions = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')


    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    UNIT_CHOICES = [
        ('tsp', 'Teaspoon'),
        ('tbsp', 'Tablespoon'),
        ('cup', 'Cup'),
        ('1/2 cup', '½ Cup'),
        ('1/4 cup', '¼ Cup'),
        ('g', 'Gram'),
        ('kg', 'Kilogram'),
        ('ml', 'Milliliter'),
        ('l', 'Liter'),
        ('oz', 'Ounce'),
        ('lb', 'Pound'),
        ('unit', 'Unit (e.g. 1 egg)'),
    ]

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.ingredient.name}"

