# Recipe Book (Django)

A simple recipe manager with user accounts, recipe CRUD, tags, categories, ingredients formset, and image uploads.

## Features

- Register/Login (crispy-forms with Bootstrap 5)
- Recipe list, detail, create, update, delete
- Ingredient inline formset with add/remove and validation (min 1)
- Tags, categories, cooking time/unit
- User profiles with user’s recipes
- Image upload + admin image preview
- Namespaced URLs (recipes:...)

## Tech Stack

- Python 3.13+
- Django 5.2
- Bootstrap 5.3 (CDN)
- django-crispy-forms + crispy-bootstrap5
- Pillow (image support)
- SQLite (dev)

## Quickstart (Windows)

```powershell
# Clone
git clone <this-repo-url> recipebook
cd recipebook

# Virtual env
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install deps
pip install Django==5.2.4 crispy-forms crispy-bootstrap5 Pillow

# Migrate DB
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser

# Run
python manage.py runserver
```

## Project Setup Notes

- settings.py
  - INSTALLED_APPS includes: crispy_forms, crispy_bootstrap5, recipes
  - CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap5",)
  - CRISPY_TEMPLATE_PACK = "bootstrap5"
  - LOGIN_REDIRECT_URL = "recipes:recipe_list"
  - LOGOUT_REDIRECT_URL = "recipes:recipe_list"
  - MEDIA_URL = "/media/", MEDIA_ROOT = BASE_DIR / "media"
- urls.py (project)
  - path("", include("recipes.urls", namespace="recipes"))
  - static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) in DEBUG

## Important URL Names

- recipes:recipe_list
- recipes:recipe_detail (pk)
- recipes:recipe_create
- recipes:recipe_update (pk)
- recipes:recipe_delete (pk)
- recipes:login, recipes:logout, recipes:register
- recipes:profile (username)

## Templates

- Base layout includes Bootstrap 5 + Select2 CSS/JS (CDN)
- Logout (Django 5) must be POST:

```html
<form method="post" action="{% url 'recipes:logout' %}">
  {% csrf_token %}
  <button class="btn btn-outline-secondary" type="submit">Logout</button>
</form>
```

- Navbar toggler icon uses local static: /static/icons8-burger-50.png

## Static & Media

- Place custom CSS in recipes/static/css/styles.css
- Place images in media/ (ignored by git)
- Dev serving enabled via static() in project urls

## Admin

- Recipes inline their ingredients (ingredient, quantity, unit)
- Image preview shown in admin

## Git Ignore

- media/, _.json,_.sqlite3, \*.db, venvs, **pycache**, .vscode, etc. (see .gitignore)

## Troubleshooting

- NoReverseMatch: ensure namespaced URLs in templates (recipes:recipe_list)
- Logout 405: use POST form (see above)
- Navbar burger not toggling: ensure bootstrap.bundle.min.js is loaded and data-bs-target="#navbarMain" matches the collapse id

## License

Unlicensed/private by default. Add a LICENSE
