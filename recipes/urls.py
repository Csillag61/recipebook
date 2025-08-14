from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

app_name = "recipes"

urlpatterns = [
    path("", views.recipe_list, name="recipe_list"),
    path("recipes/", RedirectView.as_view(pattern_name="recipes:recipe_list", permanent=False)),
    path("recipe/<int:pk>/", views.recipe_detail, name="recipe_detail"),
    path("recipe/new/", views.recipe_create, name="recipe_create"),
    path("recipe/<int:pk>/edit/", views.recipe_update, name="recipe_update"),  # edit
    # Auth
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="recipes/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="recipes:recipe_list"), name="logout"),
    # Profile
    path("profile/<str:username>/", views.profile, name="profile"),
    path("recipe/<int:pk>/delete/", views.recipe_delete, name="recipe_delete"),
]
