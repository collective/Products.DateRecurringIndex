===========================
Products.DateRecurringIndex
===========================

A Zope 2 catalog index with support for indexing of recurring events, following
the icalendar standard. It is a drop-in replacement for the Zope2 DateIndex and
will produce the same results for non-recurring dates.

The DateRecurringIndex accepts following parameters:

id
    Required. The name of the field or object attribute to be indexed.

recurdef
    Required. The name of the object attribute, which returns the icalendar
    rrule (recurrence rule) string.

until
    Optional. The name of the objects attribute, which returns the date, until
    the recurrence should happen. The recurrence definition can also contain an
    UNTIL component. If both are defined, the recurrence calculation stops 
    whenever the first until-date is met. If not given at all, there is a
    MAXCOUNT ceiling constant, defined in plone.event.recurrence, which defines
    the maximum number of occurences.


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

* Jens Klein <jens@bluedynamics.com> - Original implementation.

* Johannes Raggam <johannes@raggam.co.at> - Refactoring for icalendar rrrule
  support.

* Copyright 2008-2012, BlueDynamics Alliance, Austria

* under BSD License derivative
