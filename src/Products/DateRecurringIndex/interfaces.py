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
