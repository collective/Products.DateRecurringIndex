# -*- coding: utf-8 -*-
import doctest
import unittest
from datetime import datetime

import pytz
from OFS.Folder import Folder
from Products.ZCatalog.Catalog import Catalog
from Products.ZCatalog.ZCatalog import ZCatalog
from zope.testing import cleanup

from Products.DateRecurringIndex.index import DateRecurringIndex

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS


class DummyEvent(object):
    """some dummy with a start, delta and until to index"""

    def __init__(self, id=None, start=None, recurdef=None, until=None):
        self.id = id
        self.start = start
        self.recurdef = recurdef
        self.until = until


class DummyExtras(object):
    def __init__(self, recurrence_type=None, recurdef=None, until=None):
        self.recurrence_type = recurrence_type
        self.recurdef = recurdef
        self.until = until


class TestIndex(cleanup.CleanUp, unittest.TestCase):
    def setUp(self):
        cleanup.CleanUp.setUp(self)

    def test_index(self):
        """Test the index in icalendar/rfc5545 recurrence mode."""
        # Initialize the catalog with DateRecurringIndex
        dri = DateRecurringIndex(
            "start",
            extra=DummyExtras(
                recurrence_type="ical", recurdef="recurdef", until="until"
            ),
        )

        # Index must have be the same name as dri's id
        cat = Catalog()
        cat.addIndex("start", dri)
        cat.addColumn("id")

        # catalog needs to be contained somewhere, otherwise
        # aquisition-wrapping of result brains doesn't work
        portal = Folder(id="portal")
        cat.__parent__ = portal

        # Let's define some dummy events and catalog them.
        cet = pytz.timezone("CET")

        # Index the same event more than once and test if index size changes.
        test_event = DummyEvent(
            id="test_event",
            start=datetime(2001, 1, 1),
            recurdef="RRULE:FREQ=DAILY;INTERVAL=1;COUNT=5",
        )
        self.assertEqual(cat.catalogObject(test_event, "test_event"), 1)
        self.assertEqual(dri.indexSize(), 5)

        test_event = DummyEvent(
            id="test_event",
            start=datetime(2001, 1, 1),
            recurdef="RRULE:FREQ=DAILY;INTERVAL=1;COUNT=3",
        )
        self.assertEqual(cat.catalogObject(test_event, "test_event"), 1)
        self.assertEqual(dri.indexSize(), 3)

        test_event = DummyEvent(
            id="test_event",
            start=datetime(2001, 1, 1),
            recurdef="RRULE:FREQ=DAILY;INTERVAL=1;COUNT=8",
        )
        self.assertEqual(cat.catalogObject(test_event, "test_event"), 1)
        self.assertEqual(dri.indexSize(), 8)

        cat.uncatalogObject("test_event")
        self.assertEqual(dri.indexSize(), 0)

        # Index for querying later on...
        nonr = DummyEvent(
            id="nonr", start=datetime(2010, 10, 10, 0, 0, tzinfo=cet))
        days = DummyEvent(
            id="days",
            start=datetime(2010, 10, 10, 0, 0, tzinfo=cet),
            recurdef="RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5",
        )
        mins = DummyEvent(
            id="mins",
            start=datetime(2010, 10, 10, 0, 0, tzinfo=cet),
            recurdef="RRULE:FREQ=MINUTELY;INTERVAL=10;COUNT=5",
        )
        dstc = DummyEvent(
            id="dstc",
            start=datetime(2010, 10, 20, 0, 0, tzinfo=cet),
            recurdef="RRULE:FREQ=HOURLY;INTERVAL=1;COUNT=7",
        )

        cat.catalogObject(nonr, "nonr")
        cat.catalogObject(days, "days")
        cat.catalogObject(mins, "mins")
        cat.catalogObject(dstc, "dstc")

        # Query min one specific date
        query = {
            "start": {
                "query": datetime(2010, 10, 10, 0, 0, tzinfo=cet),
                "range": "min",
            },
        }
        res = cat(**query)
        self.assertEqual(
            sorted([it.id for it in res]), ["days", "dstc", "mins", "nonr"]
        )

        # Query max one specific date
        query = {
            "start": {
                "query": datetime(2010, 10, 10, 0, 0, tzinfo=cet),
                "range": "max",
            },
        }
        res = cat(**query)
        self.assertEqual(
            sorted([it.id for it in res]),
            ["days", "mins", "nonr"]
        )

        # Query timerange over days and dstc set
        query = {
            "start": {
                "query": [
                    datetime(2010, 10, 11, 0, 0, tzinfo=cet),
                    datetime(2010, 11, 20, 0, 0, tzinfo=cet),
                ],
                "range": "min:max",
            },
        }
        res = cat(**query)
        self.assertEqual(sorted([brain.id for brain in res]), ["days", "dstc"])

        # Query timerange over mins set
        query = {
            "start": {
                "query": [
                    datetime(2010, 10, 10, 0, 10, tzinfo=cet),
                    datetime(2010, 10, 10, 0, 40, tzinfo=cet),
                ],
                "range": "min:max",
            },
        }
        res = cat(**query)
        self.assertEqual(sorted([brain.id for brain in res]), ["mins"])

    def test_plan(self):
        zcat = ZCatalog("catalog")
        # Initialize the catalog with DateRecurringIndex
        dri = DateRecurringIndex(
            "start",
            extra=DummyExtras(
                recurrence_type="ical", recurdef="recurdef", until="until"
            ),
        )
        # Index must have be the same name as dri's id
        cat = zcat._catalog
        cat.addIndex("start", dri)
        cat.addColumn("id")
        test_event = DummyEvent(
            id="test_event",
            start=datetime(2001, 1, 1),
            recurdef="RRULE:FREQ=DAILY;INTERVAL=1;COUNT=5",
        )
        cat.catalogObject(test_event, "test_event")
        query = {
            "start": {
                "query": datetime(2010, 10, 10, 0, 0),
                "range": "min",
            },
        }
        zcat.search(query)
        # Wrong benchmark key
        self.assertNotIn(
            "(('start', \"{'query': datetime.datetime(2010, 10, 10, 0, 0), 'range': 'min'}\"),): {",  # NOQA
            zcat.getCatalogPlan(),
        )
        # Correct benchmark key
        self.assertIn(
            """('start',): {""",
            zcat.getCatalogPlan(),
        )
