from zope.interface import Interface

class IRecurringSequence(Interface):
    """ Marker Interface for an RecurringSequence adapter
    """

class IRecurringIntSequence(Interface):
    """ Marker Interface for an interger RecurringSequence adapter
    """

class IRRule(Interface):
    """ Generic RRule Interface
    """

class IRRuleICal(IRRule):
    """ Marker interface for dateutils recurring rules
    """

class IRRuleTimeDelta(IRRule):
    """ Marker interface for timedelta recurring rules
    """
