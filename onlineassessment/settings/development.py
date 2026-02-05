from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
       'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE', 'DB_NAME'),
        'USER': os.getenv('MYSQL_USER', 'DB_USER'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD', 'DB_PASSWORD'),
        'HOST': os.getenv('MYSQL_HOST', 'localhost'),
        'PORT': os.getenv('MYSQL_PORT', '3306'),
    }
}