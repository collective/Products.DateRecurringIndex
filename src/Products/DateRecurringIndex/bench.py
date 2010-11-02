#!/usr/bin/env python

import pytz
import calendar
import unittest
from time import time
from datetime import datetime

from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure


class _BenchTestResult(unittest._TextTestResult):
    """Custom TestResult class to display the time each method consumed."""
    def startTest(self, test):
        test.start = time()
        super(_BenchTestResult, self).startTest(test)
        self.stream.write("%s " % test._testMethodName)
        self.stream.flush()

    def stopTest(self, test):
        super(_BenchTestResult, self).stopTest(test)
        test.stop = time()
        self.stream.write(' (time: %s)\n' % (test.stop - test.start))


class BenchTestRunner(unittest.TextTestRunner):
    """Overrides the TextTestRunner class so we can add the time info."""
    def _makeResult(self):
        return _BenchTestResult(self.stream, self.descriptions, self.verbosity)


class Dummy(object):
    """Some dummy with a start, delta and until attributes to index."""
    def __init__(self, id, start, recurdef, until):
        self.id = id
        self.start = start
        self.recurdef = recurdef
        self.until = until


class BenchTestCase(ztc.ZopeTestCase):
    """Benchmark TestCase for DateIndex and DateRecurringIndex."""

    def setUp(self):
        super(BenchTestCase, self).setUp()
        fiveconfigure.debug_mode = True
        import Products.Five
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.Five)
        import Products.DateRecurringIndex
        zcml.load_config('configure.zcml', Products.DateRecurringIndex)
        fiveconfigure.debug_mode = False

        # Create indexes
        extra = object()
        extra = Dummy(None, 'start', 'delta', 'until')
        extra.dst = 'adjust'
        extra.recurrence_type = 'timedelta'
        tz = pytz.timezone('CET')
        from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
        from Products.DateRecurringIndex.index import DateRecurringIndex
        self.di = DateIndex('di')
        self.dri = DateRecurringIndex('dri', extra=extra)
        self.items = []
        # Creates 365 items to be indexed
        for month, days in enumerate(calendar.mdays):
            for day in range(days):
                self.items.append(datetime(2010,month,day+1,0,0,0,0,tz))

    def benchCache(self):
        """Dummy test to cache the self.items list."""

    def benchDateIndex(self, total=1000):
        n = 0
        for x in range(total):
           for day in self.items:
               n += 1
               self.di.index_object(n, day)

    def benchDateRecurringIndex(self, total=1000):
        n = 0
        for x in range(total):
            for day in self.items:
               n += 1
               self.dri.index_object(n, day)


def bench():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BenchTestCase, prefix='bench'))
    return suite

def run():
    print 'Running benchmark:'
    unittest.main(defaultTest='Products.DateRecurringIndex.bench.bench',
                  testRunner=BenchTestRunner)

if __name__ == '__main__':
    run()
