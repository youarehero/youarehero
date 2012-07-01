from devel import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'yahsnapshot',  # Or path to database file if using sqlite3.
        'USER': 'yahsnapshot',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TEST_RUNNER = 'youarehero.test_runner.ProjectTestRunner'
SECRET_KEY = 'lalelu'

INSTALLED_APPS += ('django_jenkins', )

# for django jenkins
PROJECT_APPS = TEST_APPS

JENKINS_TASKS = (
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
#    'django_jenkins.tasks.run_pep8',
#    'django_jenkins.tasks.run_pyflakes',
    #'django_jenkins.tasks.run_jslint',
    #'django_jenkins.tasks.run_csslint',    
    'django_jenkins.tasks.run_sloccount',
)
