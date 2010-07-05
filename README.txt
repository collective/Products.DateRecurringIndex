===========================
Products.DateRecurringIndex
===========================

A Zope 2 catalog index for indexing of recurring events. Its build to replace  
the default DatetIndex of Zope 2. It will produce the same results. Therefore an 
object needs a start attribute.

The DateRecurringIndex takes two additional values into account: 

delta 
    an attribute returning the time in seconds of the interval for the
    recurring date
    
until 
    an attribute returning the date and time until the recurring should happen.
    
You can also configure the behaviour on daylight-saving (dst) border change. 
In short: On change from winter to summer 24h are added. So a recurring date -
such as an event - should happen every day 11am. Taken the example day-before + 
24h = 12am day after dst change. Usally its not wanted behaviour on human 
calendars. Therefore you can control this behaviour: ``adjust``, ``keep`` and 
``auto``. See the recurring.txt doc-test file for detailed information about it.
usally on human calendars auto work out fine, on technical calendars keep is 
the right choice.


Datetime.DateTime vs. datetime.datetime
=======================================

Inside Zope2 everybody uses DateTime.DateTime or iow the Zope-DateTime. At time 
of writing Zope-DateTime (around 1998) there was no good date/time 
implementation in python. But these days  we have a better implementation.  
Even if the pythons datetime implementation has its problems,
together with pytz for timezone handling its very mature. 

So, why is it covered here? Just because the above mentioned dst-handling works 
only if the start and until values are non-naive python datetimes. Just keep it
in mind when using this index: If you use recurring dates and you want 
dst-adjust make sure your implementation returns a python datetime. And also 
keep in mind: If youre i.e. in Austria with CET timezone, add a recurring date: 
it will look fine to you, every day at 11:00am, doesnt matter if DST or not, 
your event happens. If you go international and your event is shown in a  
different timezone - or in the same in a country without DST at all - it might 
differ and is not always at the the time.

Todo, future plans
==================

Another good person with awareness of all this datetime-problems is 
Lennart Regebro. He pointed me to dateutil.rrule which will replace 
delta-in-seconds approach in one of the next releases.

The index becomes slow (esp. on indexing time) if you have often short deltas 
for a long time (like forever). Also forever means to have a ceiling-date which
is defined as forever. Even if its difficult to implement it might be better to 
calculate the recurring values at query-time for the queried range and use them 
in the query. This isnt trivial, at query-time it has to be fast even if there 
are many 100.000 objects cataloged. If there are resources it may happen to 
implement it this way, for now we stick to pre-calculation.    


Credits
=======

* Copyright 2008-2009, BlueDynamics Alliance, Austria

* under BSD License derivative
  
* written by Jens Klein <jens@bluedynamics.com>