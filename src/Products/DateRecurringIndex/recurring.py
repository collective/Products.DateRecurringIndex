# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD derivative License

import datetime
from dateutil.rrule import rrule
from dateutil.rrule import rruleset
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
        self.rdate = None
        self.exrule = None
        self.exdate = None

class RRule(object):
    implements(IRRule)
    def __init__(self):
        self.dtstart = None
        self.interval = None
        self.wkst = None
        self.count = None
        self.until = None


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
    def __init__(self, start, recrule=None, until=None, dst=DSTAUTO, exclude=False):
        self.exclude = exclude
        if not isinstance(recrule, list) and not isinstance(recrule, tuple):
            recrule = [recrule]
        # TODO, FIXME: remove eval hack, which is an SECURITY ISSUE
        # eval is used to parse a list of strings to a list of dicts
        recrules = []
        for rr in recrule:
            if isinstance(rr, str):
                rr = eval(rr)
            recrules.append(rr)
        super(RecurConfICal, self).__init__(start, recrules, until, dst=DSTAUTO)


@adapter(IRecurConfICal)
@implementer(IRecurringSequence)
def recurringSequenceICal(recruleset):
    """ Same as RecurringSequence from dateutil.rrule rules
    """
    rset = rruleset()
    # TODO: shorten and clearify following comment
    rset.rdate(recruleset.start) # always include the base date. this could may
    # be problematic, if value of the index' start attribute is not meant to be
    # the base date of an event but the starting date of the recurrence _and_
    # the first calculated occurence differs from the base date.
    # this should just rarely be the case.
    for recrule in recruleset.recrule:
        if 'dtstart' not in recrule or not recrule['dtstart']:
            recrule['dtstart'] = recruleset.start
        recrule['dtstart'] = anydt(recrule['dtstart'])

        if 'until' not in recrule or not recrule['until']:
            recrule['until'] = recruleset.until
        recrule['until'] = anydt(recrule['until'])

        if 'freq' not in recrule:
            recrule['freq'] = None

        exclude = False
        if 'exclude' in recrule:
            exclude = recrule['exclude']
            del recrule['exclude']

        if recrule['freq'] is None and not exclude:
            rset.rdate(recrule['dtstart'])
        elif recrule['freq'] is None and exclude:
            rset.exdate(recrule['dtstart'])
        elif exclude:
            rset.exrule(rrule(**recrule))
        else:
            rset.rrule(rrule(**recrule))

    # TODO: äh?
    if recruleset.start not in list(rset):
        rset

    return rset


@adapter(IRecurConfTimeDelta)
@implementer(IRecurringSequence)
def recurringSequenceTimeDelta(recurdef):
    """a sequence of integer objects.

    @param recurdef.start: a python datetime (non-naive) or Zope DateTime.
    @param recurdef.recrule: Timedelta as integer >=0 (unit is minutes) or None.
    @param recurdef.until: a python datetime (non-naive) or Zope DateTime >=start or None.
    @param recurdef.dst: is either DSTADJUST, DSTKEEP or DSTAUTO. On DSTADJUST we have a
                more human behaviour on daylight saving time changes: 8:00 on
                day before spring dst-change plus 24h results in 8:00 day after
                dst-change, which means in fact one hour less is added. On a
                recurdef.recrule < 24h this will fail!
                If DSTKEEP is selected, the time is added in its real hours, so
                the above example results in 9:00 on day after dst-change.
                DSTAUTO uses DSTADJUST for >=24h and DSTKEEP for < 24h
                recurdef.recrule delta minutes.

    @return: a sequence of dates
    """
    start = recurdef.start
    delta = recurdef.recrule
    until = recurdef.until
    dst = recurdef.dst

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
