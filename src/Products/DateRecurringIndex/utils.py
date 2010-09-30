# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD derivative License

import pytz
import datetime
from DateTime import DateTime

utctz = pytz.timezone('UTC')

# TODO: let guesstz guess the time zone not via zope's DateTime
def guesstz(DT):
    """'Guess' pytz from a zope DateTime.

    !!! theres no real good method to guess the timezone.
    DateTime was build somewhere in 1998 long before python had a working
    datetime implementation available and still stucks with this incomplete
    implementation.
    """
    if DT.timezoneNaive():
        return utctz
    tzname = DT.timezone()

    #    # DateTime timezones not fully compatible with pytz
    #    # see http://pypi.python.org/pypi/DateTime/2.12.0
    #    if tzname.startswith('GMT'):
    #        tzname = 'Etc/%s' % tzname
    try:
        tz = pytz.timezone(tzname)
        return tz
    except KeyError:
        pass
    return None


def pydt(dt):
    """converts a zope DateTime in a python datetime.
    """
    if dt is None:
        return None

    if isinstance(dt, datetime.datetime):
        return dt.replace(tzinfo=dt.tzinfo.normalize(dt).tzinfo)

    tz = guesstz(dt)
    if tz is None:
        dt = dt.toZone('UTC')
        tz = utctz

    year, month, day, hour, min, sec = dt.parts()[:6]
    # seconds (parts[6]) is a float, so we map to int
    sec = int(sec)
    dt = datetime.datetime(year, month, day, hour, min, sec, tzinfo=tz)
    dt = dt.tzinfo.normalize(dt)
    return dt

def utc(dt):
    """convert python datetime to UTC."""
    if dt is None:
        return None
    return dt.astimezone(utctz)

def dt2int(dt):
    """calculates an integer from a datetime.

    resolution is one minute, always relative to utc
    """
    if dt is None:
        return 0
    # TODO: if dt has not timezone information, guess and set it
    dt = utc(dt)
    value = (((dt.year*12+dt.month)*31+dt.day)*24+dt.hour)*60+dt.minute
    return value

def int2dt(dtint):
    """returns a datetime object from an integer representation with
    resolution of one minute, relative to utc
    """
    if not isinstance(dtint, int):
        raise ValueError, 'int2dt expects integer values as arguments.'
    minutes = dtint % 60
    hours = dtint / 60 % 24
    days = dtint / 60 / 24 % 31
    months = dtint / 60 / 24 / 31 % 12
    years = dtint / 60 / 24 / 31 / 12
    return datetime.datetime(years, months, days, hours, minutes, tzinfo=pytz.timezone('UTC'))


def anydt(dt):
    """ Tries to convert a string to a datetime object
    """
    if dt is None:
        return None
    if not isinstance(dt, datetime.datetime):
        # TODO:!!! try to use datetime directly instead of converting it from
        # DateTime. The reason for this is, that DateTime sets the timezone
        # to something set via zope.conf (really?) or set by the server
        if not isinstance(dt, DateTime):
            dt = DateTime(dt)
        dt = pydt(dt)
    return dt
