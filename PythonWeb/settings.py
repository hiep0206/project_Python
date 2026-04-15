import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-$fpah!c_%m@&nz1%#mvhn-8v6_agx$cv1@sns9(i6ovfrsd$l^'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Các app của bạn
    'shop',      
    'orders',    
    'home',      
    'blog',      
    'blogger',
       
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

ROOT_URLCONF = 'PythonWeb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Đưa các đường dẫn template vào đây để Django tìm thấy file HTML của bạn
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'home' / 'templates',
            BASE_DIR / 'blog' / 'templates',
            BASE_DIR / 'shop' / 'templates',
            BASE_DIR / 'orders' / 'templates', # THÊM DÒNG NÀY ĐỂ NHẬN FILE THANH TOÁN
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processors.cart', # Giúp hiện số lượng giỏ hàng ở mọi nơi
            ],
        },
    },
]

WSGI_APPLICATION = 'PythonWeb.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",           # Thư mục static ngoài cùng
    BASE_DIR / "home" / "static",  # Thư mục static của app home
    BASE_DIR / "shop" / "static",  # THÊM DÒNG NÀY để nhận CSS của shop
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Key dùng để lưu trữ giỏ hàng trong Session
CART_SESSION_ID = 'cart'