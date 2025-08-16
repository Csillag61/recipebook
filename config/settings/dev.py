from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.sqlite3',
       'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
   }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Optional dev-only apps (enable if installed)
try:
    import debug_toolbar  # type: ignore

    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]
except Exception:
    pass
