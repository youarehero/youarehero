import os
settings_dir = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(settings_dir), '../../'))

# Django settings for youarehero project.
from django.core.urlresolvers import reverse_lazy

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
    )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',  # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de'

ugettext = lambda s: s
LANGUAGES = (
    ('de', ugettext('German')),
    ('en', ugettext('English')),
    )

LOCALE_PATHS = (os.path.join(PROJECT_ROOT, 'src', 'locale'), )

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

FORMAT_MODULE_PATH = 'youarehero.formats'

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.realpath(os.path.join(PROJECT_ROOT, "media"))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'


# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.realpath(os.path.join(PROJECT_ROOT, "static"))
ASSET_ROOT = os.path.realpath(os.path.join(PROJECT_ROOT, "assets"))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    )

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
    )

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'herobase.middleware.IsMobileMiddleware'
    )

ROOT_URLCONF = 'youarehero.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'youarehero.wsgi.application'

TEMPLATE_DIRS = (
    # Listed here so we have a higher priority than the native admin templates
    # for the registration/* templates
    os.path.join(PROJECT_ROOT, 'src', 'herobase', 'templates'),
# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.contrib.messages.context_processors.messages",
                               'django.core.context_processors.request',
                               'herobase.context_processors.login_form',
                               'herobase.context_processors.butler_text',
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'django.contrib.comments',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    #'rosetta',
    'endless_pagination',
    'south',
    'django_extensions',
    'south',
    'registration',
    'crispy_forms',
    'autocomplete_light',
    'django_filters',
    # 'easy_maps',
    'easy_thumbnails',
    'django_google_maps',
    'activelink',

    # project specific installed apps
    'herobase',
    'heromessage',
    'herorecommend',
    'heronotification',
    'heroorganization',
    'heroachievements',
    'herocoupon',
)

TEST_APPS = (
    'herobase',
    'heromessage',
    'herorecommend',
    'heronotification',
    'heroorganization',
    'heroachievements',
    'herocoupon',
)

ACCOUNT_ACTIVATION_DAYS = 7


LOGIN_REDIRECT_URL = reverse_lazy('home')
EASY_MAPS_GOOGLE_KEY = 'AIzaSyAIxdNoZy_insQdebICwE4nNa9ZHNNVNfg'


TEST_RUNNER = 'youarehero.test_runner.ProjectTestRunner'

COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$',
    ]

COVERAGE_MODULE_EXCLUDES += filter(lambda x: x not in TEST_APPS, INSTALLED_APPS)

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "coverage")

HTML_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "coverage")
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s - %(funcName)s: %(message)s'
        },
        'precise': {
            'format': '[%(levelname)s %(asctime)s %(process)d %(thread)d] [%(name)s %(funcName)s] %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'formatter': 'simple',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'youarehero': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

for app in TEST_APPS:
    LOGGING['loggers'][app] = {
            'handlers': ['console'],
            'level': 'DEBUG',
    }

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd61xtu1&-efpp(ym-oy6h+3rk^m_l0(5qqw=(3h7u^a(p+ofp9'

AUTH_PROFILE_MODULE = 'herobase.UserProfile'

CRISPY_FAIL_SILENTLY = not DEBUG

THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (260, 260)},
        },
    }

AUTHENTICATION_BACKENDS = ('herobase.backends.DjangoModelBackend',
                           'herobase.backends.EmailAuthBackend',
                           )


ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: "/profile/public/%s/" % u.username,
    }

FACEBOOK_APP_ID = "166151690232037"
FACEBOOK_SHOW_SEND = "true"   # or "false, default is "true"
FACEBOOK_LIKE_WIDTH = "450"   # "numeric value for width", default is 450
FACEBOOK_SHOW_FACES = "true"  # or "false, default is "true"
#FACEBOOK_FONT = "font"        # default is "arial"
