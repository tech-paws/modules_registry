#pylint: disable = all
from tech_paws.modules_registry.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
SECRET_KEY = 'demo'
DEBUG = True
ALLOWED_HOSTS = ['*']
