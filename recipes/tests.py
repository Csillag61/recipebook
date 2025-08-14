from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse

from .models import Recipe, Category


class RecipeViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Users
        cls.author = User.objects.create_user(username="alice", password="pass1234")
        cls.other = User.objects.create_user(username="bob", password="pass1234")

        cls.category = Category.objects.create(name="Dinner")

        # Provide required fields
        cls.recipe = Recipe.objects.create(
            title="Test Recipe",
            author=cls.author,
            category=cls.category,
            cooking_time=0,  # required field
            # cooking_time_unit="min",  # uncomment if your model requires a unit
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
        # The page should render the author's username
        self.assertContains(resp, self.author.username)

    def test_create_requires_login(self):
        url = reverse("recipes:recipe_create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("recipes:login"), resp.url)

    def test_update_requires_login(self):
        url = reverse("recipes:recipe_update", args=[self.recipe.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("recipes:login"), resp.url)

    def test_delete_requires_login(self):
        url = reverse("recipes:recipe_delete", args=[self.recipe.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("recipes:login"), resp.url)

    def test_only_author_can_update(self):
        self.client.login(username="bob", password="pass1234")
        url = reverse("recipes:recipe_update", args=[self.recipe.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_only_author_can_delete(self):
        self.client.login(username="bob", password="pass1234")
        url = reverse("recipes:recipe_delete", args=[self.recipe.pk])
        # GET shows confirm page for authors only; others should get 403 even on GET
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_author_can_delete_with_post(self):
        self.client.login(username="alice", password="pass1234")
        url = reverse("recipes:recipe_delete", args=[self.recipe.pk])
        # Confirm page (GET)
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        self.assertTemplateUsed(resp_get, "recipes/recipe_confirm_delete.html")
        # Delete (POST)
        resp = self.client.post(url, follow=True)
        self.assertRedirects(resp, reverse("recipes:recipe_list"))
        self.assertFalse(Recipe.objects.filter(pk=self.recipe.pk).exists())

    def test_logout_is_post_only(self):
        # Django 5+ LogoutView rejects GET with 405
        url = reverse("recipes:logout")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 405)

    def test_namespaced_urls_exist(self):
        # Smoke test for critical URL names
        names = [
            "recipes:recipe_list",
            "recipes:recipe_detail",
            "recipes:recipe_create",
            "recipes:login",
            "recipes:register",
            "recipes:profile",
        ]
        for name in names:
            # recipe_detail needs an arg; skip it here
            if name.endswith("recipe_detail"):
                reverse(name, args=[self.recipe.pk])
            elif name.endswith("profile"):
                reverse(name, args=[self.author.username])


