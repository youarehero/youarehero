# -*- coding: utf-8 -*-
import StringIO
from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner
from django_coverage.coverage_runner import CoverageRunner

# TODO write something that generates a coverage folder if it doesn't already exist


import time
import sys
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.agile import PythonTracebackLexer

try:
    import unittest2 as unittest
    from unittest2 import result
except ImportError:
    import unittest
    from unittest import result


def colored(text, color):
    return u'\033[0;%sm%s\033[0;m' % (color, text)

def red(text):
    return colored(text, 31)

def green(text):
    return colored(text, 32)

def grey(text):
    return colored(text, 30)

bar = '-' * 79 + '\n'


class TextTestResult(result.TestResult):
    """A test result class that can print formatted text results to a stream.
    """

    def __init__(self, stream, descriptions, verbosity):
        super(TextTestResult, self).__init__()
        self.stream = stream

        self.verbosity = verbosity
        self.descriptions = descriptions
        self._last_output_len = 0


    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return '\n'.join((str(test), doc_first_line))
        else:
            return str(test)

    def _suppressStderr(self):
        self._sys_stderr = sys.stderr
        sys.stderr = StringIO.StringIO()

    def _resumeStderr(self, silent=False):
        if not silent:
            content = sys.stderr.getvalue()
            if content:
                self.stream.write(grey(sys.stderr.getvalue()))
                self.stream.writeln()
        sys.stderr.close()
        sys.stderr = self._sys_stderr

    def startTest(self, test):
        self._suppressStderr()
        super(TextTestResult, self).startTest(test)
        self.start_time = time.time()
        module_name = str(test.__class__.__module__)
        class_name = str(test.__class__.__name__)

        same_module = getattr(self, '_last_module_name', None) == module_name
        same_class = getattr(self, '_last_class_name', None) == class_name
        self._last_module_name = module_name
        self._last_class_name = class_name

        if not same_module:
            self.stream.writeln("\n  " + module_name)
        if not same_class:
            if same_module:
                self.stream.writeln()
            self.stream.writeln("    " + class_name)

        self.printTestDescription(test, u"↻", clearable=True)

    def printTestDescription(self, test, prepend="", append="", clearable=False):
        test_description = test.shortDescription()
        test_name = str(test._testMethodName)

        output = u"      %s " % (prepend,)

        if test_description:
            output += u"%s (%s) " % (test_description, grey(test_name))
        else:
            output += u"%s " % (test_name, )

        output += append
        if self._last_output_len:
            self.stream.write('\r')
        self._last_output_len = len(output)
        if clearable:
            self.stream.write(output.encode('utf-8'))
        else:
            self.stream.writeln(output.encode('utf-8'))

    def getDuration(self):
            return "(%d ms)" % (1000 * (time.time() - self.start_time))

    def addSuccess(self, test):
        super(TextTestResult, self).addSuccess(test)
        self.printTestDescription(test, green(u"✔"), green(self.getDuration()))
        self._resumeStderr()

    def addError(self, test, err):
        super(TextTestResult, self).addError(test, err)
        self.printTestDescription(test, red(u"✗"), append=red("(error)"))
        self._resumeStderr()


        # self.stream.write(red(err))

    def addFailure(self, test, err):
        super(TextTestResult, self).addFailure(test, err)
        self.printTestDescription(test, red(u"✗"), red("(failed)"))
        self._resumeStderr()

    def addSkip(self, test, reason):
        super(TextTestResult, self).addSkip(test, reason)
        self.printTestDescription(test, grey(u"→"), grey("(skipped)"))
        self._resumeStderr()

    def addExpectedFailure(self, test, err):
        super(TextTestResult, self).addExpectedFailure(test, err)
        self.stream.writeln("expected failure")
        self._resumeStderr()

    def addUnexpectedSuccess(self, test):
        super(TextTestResult, self).addUnexpectedSuccess(test)
        self.stream.writeln("unexpected success")
        self._resumeStderr()

    def printErrors(self):
        self.stream.writeln()
        self.printErrorList(self.errors)
        # self.printErrorList(self.failures)

    def printErrorList(self, errors):
        self.stream.writeln(red("Errors: %d" % len(errors)))
        for test, err in errors:
            self.stream.writeln(test.shortDescription())
            for line in highlight(err, PythonTracebackLexer(), TerminalFormatter(bg='light')).split('\n'):
                self.stream.write('      ')
                self.stream.writeln(line)


class ProjectTestRunner(DjangoTestSuiteRunner):
    def run_suite(self, suite, **kwargs):
        return unittest.TextTestRunner(
            verbosity=self.verbosity,
            failfast=self.failfast,
            resultclass=TextTestResult
            ).run(suite)


    def build_suite(self, test_labels, *args, **kwargs):
        return super(ProjectTestRunner, self).build_suite(test_labels or
                [a.rsplit('.',1)[-1] for a in settings.TEST_APPS], *args, **kwargs)

class ProjectCoverageRunner(ProjectTestRunner, CoverageRunner):
    pass
