import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-a4yv8i(6_!*24s9rpnai(m=l-lb4b06)m7byg8fx%nh9(t%e=#')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Allow all render subdomains and locals
ALLOWED_HOSTS = ['travelgo-django.onrender.com', 'localhost', '127.0.0.1', '.onrender.com']
DEBUG = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'corsheaders',
    'rest_framework',
    'whitenoise.runserver_nostatic',
    
    # Your App
    'flights',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',           # 1. MUST be at the very top
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',      # 2. For Static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',       # 3. MUST be after CorsMiddleware
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'travelgo_django.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'travelgo_django.wsgi.application'

# Database
# Note: On Render Free Tier, this file will be wiped every time the server restarts.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# For extra safety, allow Whitenoise to compress and cache files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --------------------------------------------------------------------------
# PRODUCTION SECURITY & CORS SETTINGS
# --------------------------------------------------------------------------

# IMPORTANT: I REMOVED CORS_REPLACE_HTTPS_REFERER TO FIX THE E013 ERROR.
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://travelgo-front.onrender.com",
]

CORS_ALLOW_CREDENTIALS = True

# Required for Django 4.0+ when hosted on HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://travelgo-django.onrender.com',
    'https://travelgo-front.onrender.com'
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------------
# EMAIL SYSTEM CONFIGURATION
# --------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465               
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True  
EMAIL_HOST_USER = 'lalit.lakshmipathi@gmail.com'
EMAIL_HOST_PASSWORD = 'uydn mijd uktm qsdh'
DEFAULT_FROM_EMAIL = 'lalit.lakshmipathi@gmail.com'
APPEND_SLASH = True