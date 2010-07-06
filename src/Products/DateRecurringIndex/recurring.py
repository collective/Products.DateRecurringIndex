# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD derivative License

import datetime
import dateutil
from utils import pydt
from utils import dt2int
from utils import utc
from utils import anydt

from zope.interface import implements
from zope.interface import implementer
from zope.component import adapter

from Products.DateRecurringIndex.interfaces import IRecurringSequence
from Products.DateRecurringIndex.interfaces import IRecurringIntSequence
from Products.DateRecurringIndex.interfaces import (
    IRecurConf,
    IRecurConfICal,
    IRecurConfTimeDelta,
    IRRuleSet,
    IRRule
)

DSTADJUST = 'adjust'
DSTKEEP   = 'keep'
DSTAUTO   = 'auto'


class RRuleSet(object):
    implements(IRRuleSet)
    def __init__(self):
        self.rrules = None
        self.rdates = None
        self.exrules = None
        self.exdates = None

class RRule(object):
    """ dateutil.rrule data structures.
    FAQ
    ===
    Question: Why not using dateutil.rrule instances?
    Answer: We don't want to store dateutil.rrule instances on
            recurrence-definition-fields
    """
    implements(IRRule)
    def __init__(self):
        self.freq = None
        self.dtstart = None
        self.interval = None
        self.wkst = None
        self.count = None
        self.until = None

    @attribute
    def rrule(self):
        rrule = dateutil.rrule(
            self.freq,
            dtstart = self.dtstart,
            interval = self.interval,
            wkst = self.wkst,
            count = self.count,
            until = self.until)
        return rrule

class RecurConf(object):
    """RecurrenceRule object"""
    def __init__(self, start, recrule=None, until=None, dst=DSTAUTO):
        self._start = None
        self._until = None
        self.start = start
        self.recrule = recrule
        self.until = until
        self.dst = dst

    def get_start(self):
        return self._start
    def set_start(self, start):
        self._start = anydt(start)
    start = property(get_start, set_start)

    def get_until(self):
        return self._until
    def set_until(self, until):
        self._until = anydt(until)
    until = property(get_until, set_until)

class RecurConfTimeDelta(RecurConf):
    implements(IRecurConfTimeDelta)

class RecurConfICal(RecurConf):
    implements(IRecurConfICal)


@adapter(IRecurConfICal)
@implementer(IRecurringSequence)
def recurringSequenceICal(recurconf):
    """ Same as RecurringSequence from dateutil.rrule rules
    """
    rset = dateutil.rruleset()
    rset.rdate(recurconf.start) # always include the start date itself

    if not recurconf.recrule:
        return rset
    rrules = recurconf.recrule.rrules
    exrules = recurconf.recrule.exrules
    rdates = recurconf.recrule.rdates
    exdates = recurconf.recrule.exdates

    if rrules and isinstance(list, rrules):
        for rrule in rrules:
            rset.rrule(rrule.rrule)
    if exrules and isinstance(list, exrules):
        for exrule in exrules:
            rset.exrule(exrule.rrule)
    if rdates and isinstance(list, rdates):
        for rdate in rdates:
            rset.rdate(rdate)
    if exdates and isinstance(list, exdates):
        for exdate in exdates:
            rset.exdate(exdate)

    return rset


@adapter(IRecurConfTimeDelta)
@implementer(IRecurringSequence)
def recurringSequenceTimeDelta(recurconf):
    """a sequence of integer objects.

    @param recurconf.start: a python datetime (non-naive) or Zope DateTime.
    @param recurconf.recrule: Timedelta as integer >=0 (unit is minutes) or None.
    @param recurconf.until: a python datetime (non-naive) or Zope DateTime >=start or None.
    @param recurconf.dst: is either DSTADJUST, DSTKEEP or DSTAUTO. On DSTADJUST we have a
                more human behaviour on daylight saving time changes: 8:00 on
                day before spring dst-change plus 24h results in 8:00 day after
                dst-change, which means in fact one hour less is added. On a
                recurconf.recrule < 24h this will fail!
                If DSTKEEP is selected, the time is added in its real hours, so
                the above example results in 9:00 on day after dst-change.
                DSTAUTO uses DSTADJUST for >=24h and DSTKEEP for < 24h
                recurconf.recrule delta minutes.

    @return: a sequence of dates
    """
    start = recurconf.start
    delta = recurconf.recrule
    until = recurconf.until
    dst = recurconf.dst

    start = pydt(start)

    if delta is None or delta < 1 or until is None:
        yield start
        return

    assert(dst in [DSTADJUST, DSTKEEP, DSTAUTO])
    if dst==DSTAUTO and delta<24*60:
        dst = DSTKEEP
    elif dst==DSTAUTO:
        dst = DSTADJUST

    until = pydt(until)
    delta = datetime.timedelta(minutes=delta)
    yield start
    before = start
    while True:
        after = before + delta
        if dst==DSTADJUST:
            after = after.replace(tzinfo=after.tzinfo.normalize(after).tzinfo)
        else:
            after = after.tzinfo.normalize(after)
        if utc(after) > utc(until):
            break
        yield after
        before = after


@adapter(IRecurConf)
@implementer(IRecurringIntSequence)
def recurringIntSequence(recrule):
    """ Same as recurringSequence, but returns integer represetations of dates.
    """
    recseq = IRecurringSequence(recrule)
    for dt in recseq:
        yield dt2int(dt)
