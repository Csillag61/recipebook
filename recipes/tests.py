from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Recipe, Category, Ingredient, RecipeIngredient


class RecipeViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username="alice", password="pass1234")
        cls.other = User.objects.create_user(username="bob", password="pass1234")
        cls.category = Category.objects.create(name="Dinner")
        cls.ingredient = Ingredient.objects.create(name="Flour")

        cls.recipe = Recipe.objects.create(
            title="Test Recipe",
            author=cls.author,
            category=cls.category,
            story="s",
            cooking_time=0,
            cooking_time_unit="min",
            instructions="do",
        )
        cls.existing_ri = RecipeIngredient.objects.create(
            recipe=cls.recipe, ingredient=cls.ingredient, quantity=100, unit="g"
        )

    def test_recipe_list_ok(self):
        url = reverse("recipes:recipe_list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "recipes/recipe_list.html")

    def test_recipe_detail_ok(self):
        url = reverse("recipes:recipe_detail", args=[self.recipe.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "recipes/recipe_detail.html")
        self.assertContains(resp, self.recipe.title)

    def test_profile_ok(self):
        url = reverse("recipes:profile", args=[self.author.username])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "recipes/profile.html")
        self.assertContains(resp, self.author.username)

    def test_create_requires_login(self):
        url = reverse("recipes:recipe_create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("recipes:login"), resp["Location"])

    def test_update_requires_login(self):
        url = reverse("recipes:recipe_update", args=[self.recipe.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("recipes:login"), resp["Location"])

    def test_delete_requires_login(self):
        url = reverse("recipes:recipe_delete", args=[self.recipe.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("recipes:login"), resp["Location"])

    def test_only_author_can_update(self):
        self.client.login(username="bob", password="pass1234")
        url = reverse("recipes:recipe_update", args=[self.recipe.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_only_author_can_delete(self):
        self.client.login(username="bob", password="pass1234")
        url = reverse("recipes:recipe_delete", args=[self.recipe.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_author_can_delete_with_post(self):
        self.client.login(username="alice", password="pass1234")
        url = reverse("recipes:recipe_delete", args=[self.recipe.pk])
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        resp = self.client.post(url, follow=True)
        self.assertRedirects(resp, reverse("recipes:recipe_list"))
        self.assertFalse(Recipe.objects.filter(pk=self.recipe.pk).exists())

    def test_logout_is_post_only(self):
        url = reverse("recipes:logout")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 405)

    def test_namespaced_urls_exist(self):
        reverse("recipes:recipe_list")
        reverse("recipes:recipe_detail", args=[self.recipe.pk])
        reverse("recipes:recipe_create")
        reverse("recipes:login")
        reverse("recipes:register")
        reverse("recipes:profile", args=[self.author.username])

    def test_register_redirects_and_logs_in(self):
        url = reverse("recipes:register")
        data = {"username": "charlie", "password1": "pass-Strong123", "password2": "pass-Strong123"}
        resp = self.client.post(url, data, follow=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("recipes:recipe_list"), resp["Location"])
        resp2 = self.client.get(reverse("recipes:recipe_list"))
        self.assertTrue(resp2.wsgi_request.user.is_authenticated)

    def test_create_with_valid_formset_creates_recipe_and_ingredients(self):
        self.client.login(username="alice", password="pass1234")
        url = reverse("recipes:recipe_create")
        data = {
            "title": "Bread",
            "story": "short",
            "description": "",
            "instructions": "mix and bake",
            "cooking_time": 5,
            "cooking_time_unit": "min",
            "category": self.category.pk,
            "tags": [],
            "recipe_ingredients-TOTAL_FORMS": "1",
            "recipe_ingredients-INITIAL_FORMS": "0",
            "recipe_ingredients-MIN_NUM_FORMS": "1",
            "recipe_ingredients-MAX_NUM_FORMS": "1000",
            "recipe_ingredients-0-ingredient": str(self.ingredient.pk),
            "recipe_ingredients-0-quantity": "1",
            "recipe_ingredients-0-unit": "unit",
        }
        resp = self.client.post(url, data, follow=True)
        self.assertRedirects(resp, reverse("recipes:recipe_list"))
        self.assertTrue(Recipe.objects.filter(title="Bread").exists())
        new = Recipe.objects.get(title="Bread")
        self.assertEqual(new.recipe_ingredients.count(), 1)

    def test_create_invalid_formset_requires_ingredient(self):
        self.client.login(username="alice", password="pass1234")
        url = reverse("recipes:recipe_create")
        data = {
            "title": "No Ing",
            "story": "short",
            "description": "",
            "instructions": "do something",
            "cooking_time": 3,
            "cooking_time_unit": "min",
            "category": self.category.pk,
            "tags": [],
            "recipe_ingredients-TOTAL_FORMS": "1",
            "recipe_ingredients-INITIAL_FORMS": "0",
            "recipe_ingredients-MIN_NUM_FORMS": "1",
            "recipe_ingredients-MAX_NUM_FORMS": "1000",
            "recipe_ingredients-0-ingredient": "",
            "recipe_ingredients-0-quantity": "",
            "recipe_ingredients-0-unit": "",
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Please submit at least 1 form.")
        self.assertFalse(Recipe.objects.filter(title="No Ing").exists())

    def test_update_with_valid_formset(self):
        self.client.login(username="alice", password="pass1234")
        url = reverse("recipes:recipe_update", args=[self.recipe.pk])
        data = {
            "title": "Test Recipe Updated",
            "story": "s",
            "description": "",
            "instructions": "do more",
            "cooking_time": 7,
            "cooking_time_unit": "min",
            "category": self.category.pk,
            "tags": [],
            "recipe_ingredients-TOTAL_FORMS": "1",
            "recipe_ingredients-INITIAL_FORMS": "1",
            "recipe_ingredients-MIN_NUM_FORMS": "1",
            "recipe_ingredients-MAX_NUM_FORMS": "1000",
            "recipe_ingredients-0-id": str(self.existing_ri.pk),
            "recipe_ingredients-0-ingredient": str(self.ingredient.pk),
            "recipe_ingredients-0-quantity": "200",
            "recipe_ingredients-0-unit": "g",
        }
        resp = self.client.post(url, data, follow=True)
        self.assertRedirects(resp, reverse("recipes:recipe_list"))
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, "Test Recipe Updated")
        self.assertEqual(self.recipe.recipe_ingredients.first().quantity, 200)

    def test_update_invalid_when_deleting_last_ingredient(self):
        self.client.login(username="alice", password="pass1234")
        url = reverse("recipes:recipe_update", args=[self.recipe.pk])
        data = {
            "title": "Try Delete",
            "story": "s",
            "description": "",
            "instructions": "do",
            "cooking_time": 5,
            "cooking_time_unit": "min",
            "category": self.category.pk,
            "tags": [],
            "recipe_ingredients-TOTAL_FORMS": "1",
            "recipe_ingredients-INITIAL_FORMS": "1",
            "recipe_ingredients-MIN_NUM_FORMS": "1",
            "recipe_ingredients-MAX_NUM_FORMS": "1000",
            "recipe_ingredients-0-id": str(self.existing_ri.pk),
            "recipe_ingredients-0-ingredient": str(self.ingredient.pk),
            "recipe_ingredients-0-quantity": "100",
            "recipe_ingredients-0-unit": "g",
            "recipe_ingredients-0-DELETE": "on",
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Please submit at least 1 form.")
        self.assertTrue(RecipeIngredient.objects.filter(pk=self.existing_ri.pk).exists())

    def test_register_rejects_mismatched_passwords(self):
        url = reverse("recipes:register")
        data = {"username": "eve", "password1": "StrongPass123", "password2": "Different123"}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)  # form re-rendered with errors
        self.assertFalse(User.objects.filter(username="eve").exists())
        self.assertContains(resp, "didn’t match")  # password mismatch message

    def test_register_rejects_too_short_password(self):
        url = reverse("recipes:register")
        data = {"username": "dave", "password1": "short", "password2": "short"}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="dave").exists())
        self.assertContains(resp, "too short")

    def test_register_rejects_common_password(self):
        url = reverse("recipes:register")
        data = {"username": "erin", "password1": "password123", "password2": "password123"}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="erin").exists())
        self.assertContains(resp, "too common")

    def test_register_rejects_numeric_password(self):
        url = reverse("recipes:register")
        data = {"username": "frank", "password1": "12345678", "password2": "12345678"}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="frank").exists())
        self.assertContains(resp, "entirely numeric")

    def test_register_rejects_password_similar_to_username(self):
        url = reverse("recipes:register")
        data = {"username": "george", "password1": "george123", "password2": "george123"}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="george").exists())
        self.assertContains(resp, "too similar")


