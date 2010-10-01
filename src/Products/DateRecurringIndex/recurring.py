# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD derivative License

import datetime
from dateutil import rrule
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

MAXCOUNT  = 1000 # Maximum number of occurrences

class RecurConf(object):
    """RecurrenceRule object"""
    def __init__(self, start, recrule=None, until=None, dst=DSTAUTO, count=None):
        self._start = None
        self._until = None
        self.start = start
        self.until = until
        self.recrule = recrule
        self.dst = dst
        self.count = count

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
    @param delta: datetime.timedelta instance
    @param dstmode: is either DSTADJUST, DSTKEEP or DSTAUTO. On DSTADJUST we have a
            more human behaviour on daylight saving time changes: 8:00 on
            day before spring dst-change plus 24h results in 8:00 day after
            dst-change, which means in fact one hour less is added. On a
            recurconf.recrule < 24h this will fail!
            If DSTKEEP is selected, the time is added in its real hours, so
            the above example results in 9:00 on day after dst-change.
            DSTAUTO uses DSTADJUST for a delta >=24h and DSTKEEP for < 24h.

    """
    try:
        assert(bool(date.tzinfo))
    except:
        raise TypeError, u'Cannot normalize timezone naive dates'
    assert(dstmode in [DSTADJUST, DSTKEEP, DSTAUTO])
    if delta: assert(isinstance(delta, datetime.timedelta)) # Easier in Java
    delta = delta.seconds + delta.days*24*3600 # convert to seconds
    if dstmode==DSTAUTO and delta<24*60*60:
        dstmode = DSTKEEP
    elif dstmode==DSTAUTO:
        dstmode = DSTADJUST

    if dstmode==DSTADJUST:
        return date.replace(tzinfo=date.tzinfo.normalize(date).tzinfo)
    else: # DSTKEEP
        return date.tzinfo.normalize(date)


@adapter(IRecurConfICal)
@implementer(IRecurringSequence)
def recurringSequenceICal(recurconf):
    """ Sequence of datetime objects from dateutil's recurrence rules
    """
    start = recurconf.start
    recrule = recurconf.recrule
    dst = recurconf.dst
    until = recurconf.until
    count = recurconf.count

    # TODO: that's catched anyways when comparing both vars. Maybe leave out.
    if until:
        try:
            # start.tzinfo xnor until.tzinfo. both present or missing
            assert(not(bool(start.tzinfo) ^ bool(until.tzinfo)))
        except:
            raise TypeError, u'Timezones for both until and start have to be' \
                             + u'present or missing'

    if isinstance(recrule, rrule.rrule):
        rset = rrule.rruleset()
        rset.rrule(recrule)
    elif isinstance(recrule, rrule.rruleset):
        rset = recrule
    elif isinstance(recrule, str):
        # RFC2445 string
        # forceset: always return a rruleset
        # dtstart: optional used when no dtstart is in rfc2445 string
        #          recurconf.start is used which may be an event's endDate
        rset = rrule.rrulestr(recrule,
                             dtstart=start,
                             forceset=True
                             # compatible=True
                             )

    rset.rdate(start) # RCF2445: Always include start date

    ### Timezone normalizing and returning
    before = None
    tznaive = not start.tzinfo and True or False
    for cnt, date in enumerate(rset):
        # Limit number of recurrences otherwise calculations take too long
        if cnt+1 > MAXCOUNT: break
        if count and cnt+1 > count: break
        if until and date > until: break

        # For very first occurence which is the starting date, the timezone
        # should be correct and timezone normalizing not needed
        # For timezone naive dates there is also no need for normalizing
        if before and not tznaive:
            delta = date - before
            date = recurrence_normalize(date, delta, dst)
        yield date
        before = date
    return


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
                DSTAUTO uses DSTADJUST for a delta >=24h and DSTKEEP for < 24h.

    @return: a sequence of dates
    """
    # TODO: adjust code to recurringSequenceICal. e.g. using MAXCOUNT, count, ..
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
