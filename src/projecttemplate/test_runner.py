# Make our own testrunner that by default only tests our own apps

from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner
from django_coverage.coverage_runner import CoverageRunner

# TODO write something that generates a coverage folder if it doesn't already exist

class ProjectTestRunner(DjangoTestSuiteRunner):
    def build_suite(self, test_labels, *args, **kwargs):
        return super(ProjectTestRunner, self).build_suite(test_labels or
                [a.rsplit('.',1)[-1] for a in settings.PROJECT_APPS], *args, **kwargs)

class ProjectCoverageRunner(ProjectTestRunner, CoverageRunner):
    pass
