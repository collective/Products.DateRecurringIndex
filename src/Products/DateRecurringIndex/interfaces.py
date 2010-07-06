from zope.interface import Interface

class IRecurringSequence(Interface):
    """ Marker Interface for an RecurringSequence adapter
    """

class IRecurringIntSequence(Interface):
    """ Marker Interface for an interger RecurringSequence adapter
    """

class IRecurConf(Interface):
    """ Generic IRecurConf Interface
    """

class IRecurConfICal(IRecurConf):
    """ Marker interface for recurring definition where recrule implements
        IRRule instance and dateutil.rrule and dateutil.rset are used.
    """

class IRecurConfTimeDelta(IRecurConf):
    """ Marker interface for timedelta recurring rules
    """


class IRuleSet(Interface):
    """ Data Structure for dateutil.rset
    @ attr rrules: List of IRRule
    @ attr rdate: List of datetime instances to include
    @ attr exrule: List of IRRule for dates to exclude
    @ attr exdate: List of datetime instances to exclude
    """
class IRRule(Interface):
    """ Data Structure for datetutil.rrule
    @ attr dtstart: The recurrence start. Besides being the base for the
                    recurrence, missing parameters in the final recurrence
                    instances will also be extracted from this date. If not
                    given, datetime.now() will be used instead.
    @ attr interval: The interval between each freq iteration. For example, when using YEARLY, an interval of 2 means once every two years, but with HOURLY, it means once every two hours. The default interval is 1.
    @ attr wkst: The week start day. Must be one of the MO, TU, WE constants, or an integer, specifying the first day of the week. This will affect recurrences based on weekly periods. The default week start is got from calendar.firstweekday(), and may be modified by calendar.setfirstweekday().
    @ attr count: How many occurrences will be generated.
    @ until until: If given, this must be a datetime instance, that will specify the limit of the recurrence. If a recurrence instance happens to be the same as the datetime instance given in the until keyword, this will be the last occurrence.
    ...
    """