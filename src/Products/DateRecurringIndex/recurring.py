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
    IRecurConfTimeDelta
)

DSTADJUST = 'adjust'
DSTKEEP   = 'keep'
DSTAUTO   = 'auto'

class RecurConf(object):
    """RecurrenceRule object"""
    def __init__(self, start, recrule=None, until=None, dst=DSTAUTO):
        self._start = None
        self._until = None
        self.start = start
        self.until = until
        self.recrule = recrule
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


def recurrence_normalize(date, delta=None, dstmode=DSTADJUST):
    """Fixes invalid UTC offsets from recurrence calculations
    @param date: datetime instance to normalize.
    @param delta: integer or datetime.timedelta instance
    @param dstmode: is either DSTADJUST, DSTKEEP or DSTAUTO. On DSTADJUST we have a
            more human behaviour on daylight saving time changes: 8:00 on
            day before spring dst-change plus 24h results in 8:00 day after
            dst-change, which means in fact one hour less is added. On a
            recurconf.recrule < 24h this will fail!
            If DSTKEEP is selected, the time is added in its real hours, so
            the above example results in 9:00 on day after dst-change.
            DSTAUTO uses DSTADJUST for >=24h and DSTKEEP for < 24h
            recurconf.recrule delta minutes.

    """
    if not date.tzinfo:
        raise KeyError, u'Cannot normalize timezone naive dates'
    assert(dst in [DSTADJUST, DSTKEEP, DSTAUTO])
    if dst==DSTAUTO and delta<24*60:
        dst = DSTKEEP
    elif dst==DSTAUTO:
        dst = DSTADJUST

    if dst==DSTADJUST:
        return date.replace(tzinfo=date.tzinfo.normalize(date).tzinfo)
    else: # DSTKEEP
        return date.tzinfo.normalize(date)


@adapter(IRecurConfICal)
@implementer(IRecurringSequence)
def recurringSequenceICal(recurconf):
    """ Sequence of datetime objects from dateutil's recurrence rules
    """
    if isinstance(recurconf.recrule, dateutil.rrule.rrule):
        rset = dateutil.rrule.rruleset()
        rset.rrule(recurconf.recrule)
    elif isinstance(recurconf.recrule, dateutil.rrule.rruleset):
        rset = recurconf.recrule
    elif isinstance(recurconf.recrule, str):
        # RFC2445 string
        # forceset: always return a rruleset
        # dtstart: optional used when no dtstart is in rfc2445 string
        #          recurconf.start is used which may be an event's endDate
        rset = dateutil.rrule.rrulestr(recurconf.recrule,
                                       dtstart=recurconf.start,
                                       forceset=True
                                       # compatible=True
                                       )
    # RCF2445: Always include start date
    rset.rdate(recurconf.start)
    # TODO: check dtstart and until/count for all rrule and exrules
    #       calculating without until/count takes loooong

    # TODO: don't allwo timezone naive dates
    # No DST normalizing for timezone naive dates
    if not recurconf.start.tzinfo: return list(rset)

    # Timezone normalizing and returning
    before = None
    for date in list(rset):
        if not before:
            # very first occurence - no need for normalizing
            yield date
        else:
            delta = date - before
            date = recurrence_normalize(date, delta, dst)
            yield date
            before = date


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

    yield start
    before = start
    until = pydt(until)
    delta = datetime.timedelta(minutes=delta)
    while True:
        after = before + delta
        after = recurrence_normalize(after, delta, dst)
        if utc(after) > utc(until):
            break
        yield after
        before = after


@adapter(IRecurConf)
@implementer(IRecurringIntSequence)
def recurringIntSequence(recrule):
    """ IRecurringSequence as integer represetations of dates.
    """
    recseq = IRecurringSequence(recrule)
    for dt in recseq:
        yield dt2int(dt)
