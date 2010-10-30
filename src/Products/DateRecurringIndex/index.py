# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD derivative License

import logging
from types import IntType
from AccessControl import ClassSecurityInfo
from App.special_dtml import DTMLFile
from App.class_init import InitializeClass
from BTrees.IIBTree import IISet
from BTrees.IIBTree import union
from BTrees.IIBTree import multiunion
from BTrees.IIBTree import intersection
from BTrees.IIBTree import difference
from ZODB.POSException import ConflictError
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZCatalog.Catalog import Catalog
from Products.PluginIndexes.common import safe_callable
from Products.PluginIndexes.common.util import parseIndexRequest
from Products.PluginIndexes.common.UnIndex import UnIndex
from plone.event.utils import dt2int, pydt
from plone.event.utils import DSTADJUST, DSTAUTO, DSTKEEP
from plone.event.recurrence import (
    recurrence_int_sequence,
    recurrence_sequence_ical,
    recurrence_sequence_timedelta
)
from zope.interface import Interface
from zope.schema import Text
from zope.interface import implements
from OFS.PropertyManager import PropertyManager

logger = logging.getLogger('Products.DateRecurringIndex')

_marker = object()

VIEW_PERMISSION = 'View'
MGMT_PERMISSION = 'Manage ZCatalogIndex Entries'


class IDateRecurringIndex(Interface):
    recurrence_type = Text(title=u'Recurrence type (ical|timedelta).')
    attr_start = Text(title=u'Attribute- or fieldname of date start.')
    attr_recurdef = Text(title=u'Attribute- or fieldname of recurrence rule definition. RFC2445 compatible string or timedelta.')
    attr_until = Text(title=u'Attribute- or fieldname of date until.')
    dst = Text(title=u'Daylight saving border behaviour (adjust|keep|auto).')


class DateRecurringIndex(UnIndex, PropertyManager):
    """
    """
    implements(IDateRecurringIndex)

    meta_type="DateRecurringIndex"
    query_options = ('query', 'range')

    manage = manage_main = DTMLFile('www/addDRIndex', globals())

    _properties=({'id':'recurrence_type', 'type':'string', 'mode':'w'},
                 {'id':'attr_start', 'type':'string', 'mode':'w'},
                 {'id':'attr_recurdef', 'type':'string', 'mode':'w'},
                 {'id':'attr_until', 'type':'string', 'mode':'w'},
                 {'id':'dst', 'type':'string', 'mode':'w'},)

    manage_main._setName( 'manage_main' )
    manage_options = ( { 'label' : 'Settings'
                       , 'action' : 'manage_main'
                       },
                       {'label': 'Browse',
                        'action': 'manage_browse',
                       },
                     ) + PropertyManager.manage_options


    def __init__(self, id, ignore_ex=None, call_methods=None,
                 extra=None, caller=None):
        """ Initialize the index
            @ param extra.start:
            @ param extra.recurdef:
            @ param extral.until:
        """
        UnIndex.__init__(self, id, ignore_ex=None, call_methods=None,
                         extra=None, caller=None)
        self.recurrence_type = extra.recurrence_type
        self.attr_start = extra.start
        self.attr_recurdef = extra.recurdef
        self.attr_until = extra.until
        assert(extra.dst in [DSTADJUST, DSTKEEP, DSTAUTO])
        self.dst = extra.dst

    def index_object(self, documentId, obj, threshold=None):
        """index an object, normalizing the indexed value to an integer

           o Normalized value has granularity of one minute.

           o repeat by recurdef - wether a timedelta or a dateutil.recrule

           o take as dst handling, see recurring.py and its test for details.

           o Objects which have 'None' as indexed value are *omitted*,
             by design.
        """
        # taken partly from DateIndex
        status = 0

        try:
            start = getattr(obj, self.attr_start)
            if safe_callable(start):
                start = start()
        except AttributeError:
            # not an event
            return status

        until = getattr(obj, self.attr_until, None)
        if safe_callable(until):
            until = until()

        recurdef = getattr(obj, self.attr_recurdef, None)
        if safe_callable(recurdef):
            recurdef = recurdef()

        if self.recurrence_type == "ical":
            dates = recurrence_sequence_ical(start, recurdef, until,
                                             dst=self.dst)
        else:
            if not isinstance(recurdef, int):
                recurdef = None
            dates = recurrence_sequence_timedelta(start, recurdef, until,
                                                  dst=self.dst)

        newvalues = IISet(recurrence_int_sequence(dates))
        oldvalues = self._unindex.get(documentId, _marker)

        if oldvalues is not _marker and not difference(newvalues, oldvalues):
            return 0

        if oldvalues is not _marker:
            for oldvalue in oldvalues:
                self.removeForwardIndexEntry(oldvalue, documentId)
            if not newvalues:
                try:
                    del self._unindex[documentId]
                except ConflictError:
                    raise
                except:
                    logger.error("Should not happen: oldvalues was there,"
                                 " now it's not, for document with id %s" %
                                   documentId)
        inserted = False
        for value in newvalues:
            self.insertForwardIndexEntry( value, documentId )
            inserted = True
        if inserted:
            self._unindex[documentId] = IISet(newvalues)
            return 1
        return 0

    def unindex_object(self, documentId):
        """ carefully unindex the object with integer id 'documentId'"""

        values = self._unindex.get(documentId, None)
        if values is None:
            return
        for value in values:
            self.removeForwardIndexEntry(value, documentId)
        try:
            del self._unindex[documentId]
        except KeyError:
            logger.debug('Attempt to unindex nonexistent document id %s'
                         % documentId)

    def _apply_index( self, request, cid='', type=type ):
        """Apply the index to query parameters given in the argument

        Normalize the 'query' arguments into integer values at minute
        precision before querying.
        """
        record = parseIndexRequest( request, self.id, self.query_options )
        if record.keys == None:
            return None

        record.keys = map( pydt, record.keys )
        keys = map( dt2int, record.keys )

        index = self._index
        r = None
        opr = None

        operator = record.get( 'operator', self.useOperator )
        if not operator in self.operators :
            raise RuntimeError, "operator not valid: %s" % operator

        # depending on the operator we use intersection or union
        if operator=="or":
            set_func = union
        else:
            set_func = intersection

        # range parameter
        range_arg = record.get('range',None)
        if range_arg:
            opr = "range"
            opr_args = []
            if range_arg.find("min") > -1:
                opr_args.append("min")
            if range_arg.find("max") > -1:
                opr_args.append("max")

        if record.get('usage',None):
            # see if any usage params are sent to field
            opr = record.usage.lower().split(':')
            opr, opr_args = opr[0], opr[1:]

        if opr=="range":   # range search
            if 'min' in opr_args:
                lo = min(keys)
            else:
                lo = None

            if 'max' in opr_args:
                hi = max(keys)
            else:
                hi = None

            if hi:
                setlist = index.values(lo,hi)
            else:
                setlist = index.values(lo)

            r = multiunion(setlist)

        else: # not a range search
            for key in keys:
                set = index.get(key, None)
                if set is not None:
                    if type(set) is IntType:
                        set = IISet((set,))
                    r = set_func(r, set)

        if isinstance(r, int):
            r = IISet((r,))

        if r is None:
            return IISet(), (self.id,)
        else:
            return r, (self.id,)


    security.declareProtected(VIEW_PERMISSION, 'getRecurrenceType')
    def getRecurrenceType(self):
        return self.recurrence_type

    security.declareProtected(VIEW_PERMISSION, 'getStartAttribute')
    def getStartAttribute(self):
        return self.attr_start

    security.declareProtected(VIEW_PERMISSION, 'getRecurDefAttribute')
    def getRecurDefAttribute(self):
        return self.attr_recurdef

    security.declareProtected(VIEW_PERMISSION, 'getUntilAttribute')
    def getUntilAttribute(self):
        return self.attr_until

    security.declareProtected(VIEW_PERMISSION, 'getDSTBehaviour')
    def getDSTBehaviour(self):
        return self.dst


InitializeClass( DateRecurringIndex )

manage_addDRIndexForm = DTMLFile( 'www/addDRIndex', globals() )
def manage_addDRIndex(self, id, extra=None, REQUEST=None, RESPONSE=None,
                      URL3=None):
    """Adds a date recurring index"""
    return self.manage_addIndex(id, 'DateRecurringIndex', extra=extra,
                                  REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)