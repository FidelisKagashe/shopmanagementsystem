"""
Django settings for shopping_center project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-qvtjg8v8jqyd(w8d1u4u*k&^=f_ke86kv#-qp(g!2i6(e_xol)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.137.1','127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'csp',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shopping_center.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'shopping_center.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

from django.contrib.messages import constants as message_constants

MESSAGE_TAGS = {
    message_constants.DEBUG: 'secondary',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',  # Map 'error' to 'danger' for Bootstrap compatibility
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Dar_es_Salaam'  # Set the timezone to Tanzania's timezone

USE_I18N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Add these lines to your settings.py
MEDIA_URL = '/media/'  # URL to access media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Directory to store uploaded files

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Additional locations for static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',  # Use the 'verbose' formatter
        },
        'file': {
            'level': 'ERROR',  # Logs only ERROR and above
            'class': 'logging.FileHandler',
            'filename': 'error.log',  # File path for error logs
            'formatter': 'verbose',  # Use the 'verbose' formatter
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',  # Change to 'DEBUG' for detailed logs
            'propagate': True,
        },
        'users': {  # Replace 'api' with your actual app name
            'handlers': ['console', 'file'],
            'level': 'DEBUG',  # Capture all logs from this app
            'propagate': False,  # Avoid duplicate logging
        },
    },
}

# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'fmklinkcompany@gmail.com'  # Replace with actual email
EMAIL_HOST_PASSWORD = 'jkxb wwru lodv qier'  # Replace with actual password or app-specific password
SITE_URL = "http://localhost:8000"  # Update this to your site URL


SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database-backed sessions
SESSION_COOKIE_AGE = 3600  # Session expiry time in seconds
SESSION_SAVE_EVERY_REQUEST = True  # Optional: Refresh expiry on each request


# Ensure security by enforcing SSL (in production)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking
SECURE_CONTENT_TYPE_NOSNIFF = True

# Redirects to this page after a successful login
LOGIN_REDIRECT_URL = 'dashboard'

# Redirects here if a user tries to access a protected page and is not logged in
LOGIN_URL = 'login'

# Ensure that the session expires at the end of the browser session
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Limit session duration (optional)
SESSION_COOKIE_AGE = 7200  # 2 hour


# Other settings...

CSP_DEFAULT_SRC = ("'self'",)  # Allow resources from the same origin
CSP_SCRIPT_SRC = (
    "'self'",  # Allow scripts from the same origin
    "https://cdnjs.cloudflare.com",  # CDN for JavaScript libraries
    "https://ajax.googleapis.com",  # Google APIs for scripts
    "https://www.googletagmanager.com",  # Google Tag Manager
)

CSP_SCRIPT_SRC = ("'self'", "https://trusted-cdn.com")

CSP_STYLE_SRC = (
    "'self'",  # Allow styles from the same origin
    "https://fonts.googleapis.com",  # Google Fonts
)
CSP_FONT_SRC = (
    "'self'",  # Allow fonts from the same origin
    "https://fonts.gstatic.com",  # Google Fonts
)
CSP_IMG_SRC = (
    "'self'",  # Allow images from the same origin
    "data:",  # Allow inline images (base64)
    "https://www.youtube.com",  # Allow images from YouTube
    "https://www.instagram.com",  # Allow images from Instagram
)
CSP_FRAME_SRC = (
    "'self'",  # Allow frames from the same origin
    "https://www.youtube.com",  # Allow embedding YouTube videos
    "https://www.instagram.com",  # Allow embedding Instagram content
    "https://wa.me",  # Allow WhatsApp links
    "https://www.facebook.com",  # Allow Facebook embeds
    "https://x.com",  # Allow X (Twitter) embeds
    "https://www.adventist.org",  # Allow the Seventh-day Adventist Church website
)
CSP_CONNECT_SRC = (
    "'self'",  # Allow connections from the same origin
    "https://api.example.com",  # Example for an external API (if used)
)
