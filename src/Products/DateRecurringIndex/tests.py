import unittest
import doctest
from interlude import interact
from Testing import ZopeTestCase as ztc

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

class DummyEvent(object):
    """some dummy with a start, delta and until to index"""
    def __init__(self, id=None, start=None, recurdef=None, until=None):
        self.id = id
        self.start = start
        self.recurdef = recurdef
        self.until = until

class DummyExtras(object):
    def __init__(self, recurrence_type=None,
                 recurdef=None, until=None):
        self.recurrence_type = recurrence_type
        self.recurdef = recurdef
        self.until = until

class DRITestcase(ztc.ZopeTestCase):
    """Base TestCase for DateRecurringIndex."""

    def idsOfBrainsSorted(self, brains):
        ids = [brain.id for brain in brains]
        ids.sort()
        return ids


TESTFILES = ['index.txt',]


def test_suite():

    return unittest.TestSuite([
        ztc.ZopeDocFileSuite(
            filename,
            optionflags=optionflags,
            globs={'interact': interact,
                },
            test_class=DRITestcase
        ) for filename in TESTFILES])
