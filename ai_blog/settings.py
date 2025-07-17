from pathlib import Path
import os
from dotenv import load_dotenv

# Base project directory (where manage.py lives)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file inside BASE_DIR
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    print(f"✅ .env file found at: {ENV_PATH}")
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print(f"⚠️ .env file not found at: {ENV_PATH}")

# SECURITY: Secret Key (must be set in .env)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("Missing SECRET_KEY environment variable!")

# Debug mode toggle via environment variable (default True)
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Allowed hosts — configure as needed for production
ALLOWED_HOSTS = []

# API Keys loaded from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# Optional debug logging of keys (disable in production)
if os.getenv("DEBUG_LOG", "false").lower() == "true":
    print("🔐 OPENAI_API_KEY:", OPENAI_API_KEY)
    print("🔐 ASSEMBLYAI_API_KEY:", ASSEMBLYAI_API_KEY)

# Installed Django apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog_generator',  # Your app
]

# Middleware stack
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL configuration
ROOT_URLCONF = 'ai_blog.urls'

# Templates config
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'blog_generator' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI application path
WSGI_APPLICATION = 'ai_blog.wsgi.application'

# Database: SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JS, images)
STATIC_URL = '/static/'

STATICFILES_DIRS = []
custom_static_dir = BASE_DIR / "blog_generator" / "static"
if custom_static_dir.exists():
    STATICFILES_DIRS.append(custom_static_dir)
else:
    print(f"⚠️ WARNING: {custom_static_dir} does not exist")

STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Auth redirects
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Default auto field type for models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Optional Google service account (if used)
GOOGLE_SERVICE_ACCOUNT_FILE = BASE_DIR / "credentials" / "service_account.json"
