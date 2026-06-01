import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '1u695jxow=#k$d5e_bd$(x%2glm)z*s5h^0tt6nrgvy#8bo^jc'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'sejong_backend.apps.MongoAdminConfig',
    'sejong_backend.apps.MongoAuthConfig',
    'sejong_backend.apps.MongoContentTypesConfig',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'users',
    'elibrary',
    'info',
    'gdstorage',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sejong_backend.urls'

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

WSGI_APPLICATION = 'sejong_backend.wsgi.application'

# ─── Database ─────────────────────────────────────────────────────────────────
# Во время сборки Docker (collectstatic) БД не нужна — отключаем
if 'collectstatic' in sys.argv:
    DATABASES = {}

else:
    DATABASES = {
        "default": {
            "ENGINE": "django_mongodb_backend",
            "HOST": "mongodb+srv://dushanbe3sejong:dNZw93iCW2XeCyg5@cluster1.eiwbei3.mongodb.net",
            "NAME": "sejong_db",
            "OPTIONS": {
                "retryWrites": True,       # ← bool вместо строки "true"
                "w": "majority",
                "appName": "Cluster1",
                "serverSelectionTimeoutMS": 5000,  # ← таймаут 5 сек
                "connectTimeoutMS": 5000,
            },
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dushanbe'
USE_I18N = True
USE_TZ = True

# ─── Static files ─────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django_mongodb_backend.fields.ObjectIdAutoField'

MIGRATION_MODULES = {
    'admin': 'mongo_migrations.admin',
    'auth': 'mongo_migrations.auth',
    'contenttypes': 'mongo_migrations.contenttypes',
}

AUTH_USER_MODEL = 'users.User'

# ─── Google Drive ─────────────────────────────────────────────────────────────
# Путь к JSON ключу — BASE_DIR / 'sejong-cloud-...' гарантирует
# что файл найдётся как локально так и в Docker контейнере (/app/)
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE = str(BASE_DIR / 'sejong-cloud-ff73493133e6.json')

CSRF_TRUSTED_ORIGINS = [
    'https://sejong-app-container-847502443673.us-central1.run.app',
    'http://localhost',
    'http://127.0.0.1',
]
