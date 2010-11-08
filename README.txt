===========================
Products.DateRecurringIndex
===========================

A Zope 2 catalog index with support for indexing of recurring events. It is a
drop-in replacement for the Zope2 DateIndex and will produce the same results
for non-recurring dates.

The DateRecurringIndex accepts following parameters:

recurrence_type
    Mandatory. The type of recurrence calculation ("ical" or "timedelta").
    Mode "ical" follows the RFC2445 specification and expects RFC2445 compatible
    recurrence definition strings from the recurdef attribute.
    Mode "timedelta" expects an integer from the recurdef attribute which
    defines the minutes between each occurence. Although the same recurrence
    rule can be configured in "ical" mode, "timedelta" is faster for such
    operations.

start
    Mandatory. The name of the objects attribute, which returns the start date.

recurdef
    Mandatory. The name of the objects attribute, which returns the recurrence
    rule definitions.

until
    Optional. The name of the objects attribute, which returns the date, until
    the recurrence should happen. In "ical" mode, the recurrence definition can
    contain an UNTIL component. If not given at all, there is a MAXCOUNT ceiling
    constant, defined in plone.event.recurrence, which defines the maximum
    number of occurences.

dst
    Optional, defaults to DSTAUTO. Defines the "Daylight Saving Time" behavior
    when a daylight-saving change is in between the recurrence.
    Mode DSTADJUST: When crossing daylight saving time changes, the start time
        of the date before DST change will be the same in value as afterwards.
        It is adjusted relative to UTC. So 8:00 GMT+1 before will also result in
        8:00 GMT+2 afterwards. This is what humans might expect when recurring
        rules are defined.
    Mode DSTKEEP: When crossing daylight saving time changes, the start time of
        the date before and after DST change will be the same relative to UTC.
        So, 8:00 GMT+1 before will result in 7:00 GMT+2 afterwards. This
        behavior might be what machines expect, when recurrence rules are
        defined.
    Mode DSTAUTO:
        If the relative delta between two occurences of a reucurrence sequence
        is less than a day, DSTKEEP will be used - otherwise DSTADJUST. This
        behavior is the default.


Dependencies
============

This package is dependent on plone.event for recurrence calculations.


Datetime.DateTime vs. datetime.datetime
=======================================

Inside Zope2 everybody uses DateTime.DateTime or iow the Zope-DateTime. At time
of writing Zope-DateTime (around 1998) there was no good date/time
implementation in python. But these days  we have a better implementation.
Even if the pythons datetime implementation has its problems, together with pytz
for timezone handling it is very mature.

So, why is it covered here? Just because the above mentioned dst-handling works
only if the start and until values are non-naive python datetimes. Just keep it
in mind when using this index: If you use recurring dates and you want
dst-adjust make sure your implementation returns a python datetime. And also
keep in mind: If youre i.e. in Austria with CET timezone, add a recurring date:
it will look fine to you, every day at 11:00am, doesnt matter if DST or not,
your event happens. If you go international and your event is shown in a
different timezone - or in the same in a country without DST at all - it might
differ and is not always at the the time.


Authors
=======

* Jens Klein <jens@bluedynamics.com> - Original implementation based on
  timedelta.

* Johannes Raggam <johannes@raggam.co.at> - Datetuil RFC2445 compatible
  recurrence rules, refactoring parts into plone.event.

* Copyright 2008-2010, BlueDynamics Alliance, Austria

* under BSD License derivative
