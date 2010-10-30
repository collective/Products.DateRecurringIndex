import unittest
import doctest
from interlude import interact
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.ZCatalog.Catalog import Catalog
from Products.DateRecurringIndex.index import DateRecurringIndex
from datetime import datetime

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

class DummyEvent(object):
    """some dummy with a start, delta and until to index"""
    def __init__(self, id, start, recurdef, until):
        self.id = id
        self.start = start
        self.recurdef = recurdef
        self.until = until

class DRITestcase(ztc.ZopeTestCase):
    """Base TestCase for DateRecurringIndex."""

    def setUp(self):
        super(DRITestcase, self).setUp()
        fiveconfigure.debug_mode = True
        import Products.Five
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.Five)
        import Products.DateRecurringIndex
        zcml.load_config('configure.zcml', Products.DateRecurringIndex)
        fiveconfigure.debug_mode = False

    def afterSetUp(self):
        """set up a base scenario"""
        self.app.catalog = Catalog()
        extra = object()
        # abuse:
        extra = DummyEvent(None, 'start', 'delta', 'until') # abuse, but works
        extra.dst = 'adjust'
        extra.recurrence_type = 'timedelta'
        dri = DateRecurringIndex('recurr', extra=extra)
        self.app.catalog.addIndex('recurr', dri)
        self.app.catalog.addColumn('id')

    def buildDummies(self, cases):
        """setup dummies, cases is a list of tuples (start, delta, until)."""
        dummies = {}
        for id in cases:
            dummy = DummyEvent(id, datetime(*(cases[id][0])),
                                   cases[id][1],
                                   cases[id][2] is not None and \
                                   datetime(*(cases[id][2])) or None
                    )
            dummies[id] = dummy
        return dummies

    def catalogDummies(self, dummies):
        for id in dummies:
            self.app.catalog.catalogObject(dummies[id], id)

    def idsOfBrainsSorted(self, brains):
        ids = [brain.id for brain in brains]
        ids.sort()
        return ids


"""
@onsetup
def setup_dri():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', Products.DateRecurringIndex)
    fiveconfigure.debug_mode = False
"""
#setup_dri()
#ztc.installProduct('DateRecurringIndex')

TESTFILES = [
    'index.txt',
]

def test_suite():

    return unittest.TestSuite([
        ztc.ZopeDocFileSuite(
            filename,
            optionflags=optionflags,
            globs={'interact': interact,},
            test_class=DRITestcase
        ) for filename in TESTFILES
    ])
