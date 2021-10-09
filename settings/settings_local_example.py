from settings.settings_base import *

ALLOWED_HOSTS = ['example.org']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_name',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

DEBUG = False

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

SOCIAL_AUTH_VK_OAUTH2_ENABLED = True
SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED = True
SOCIAL_AUTH_FACEBOOK_OAUTH2_ENABLED = True
SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_ENABLED = True

SOCIAL_AUTH_VK_OAUTH2_KEY = ''
SOCIAL_AUTH_VK_OAUTH2_SECRET = ''

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''

SOCIAL_AUTH_FACEBOOK_OAUTH2_KEY = ''
SOCIAL_AUTH_FACEBOOK_OAUTH2_SECRET = ''

SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_KEY = ''
SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_SECRET = ''

if SOCIAL_AUTH_VK_OAUTH2_ENABLED:
    AUTHENTICATION_BACKENDS += ('social_core.backends.vk.VKOAuth2',)

if SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED:
    AUTHENTICATION_BACKENDS += ('social_core.backends.google.GoogleOAuth2',)

if SOCIAL_AUTH_FACEBOOK_OAUTH2_ENABLED:
    AUTHENTICATION_BACKENDS += ('social_core.backends.facebook.FacebookOAuth2',)

if SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_ENABLED:
    AUTHENTICATION_BACKENDS += ('social_core.backends.odnoklassniki.OdnoklassnikiOAuth2',)
