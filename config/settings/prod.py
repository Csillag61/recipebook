from dotenv import load_dotenv

from .base import *


DEBUG = False
ALLOWED_HOSTS = []

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
   ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


DATABASES = {
 'default': {
   'ENGINE': 'django.db.backends.postgresql',
   'NAME': os.getenv('POSTGRES_DB'),
   'USER': os.getenv('POSTGRES_USER'),
   'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
   'HOST': os.getenv('POSTGRES_HOST'),
   'PORT': os.getenv('POSTGRES_DB_PORT', 5432),
   'OPTIONS': {
     'sslmode': 'require',
   },
 }
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configure real email backend via env in production
