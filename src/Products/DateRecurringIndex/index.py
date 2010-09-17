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
from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
from Products.DateRecurringIndex.recurring import dt2int
from Products.DateRecurringIndex.recurring import pydt
from Products.DateRecurringIndex.recurring import DSTADJUST, DSTKEEP, DSTAUTO
from Products.DateRecurringIndex.recurring import RecurConfTimeDelta
from Products.DateRecurringIndex.recurring import RecurConfICal
from Products.DateRecurringIndex.interfaces import IRecurringIntSequence

logger = logging.getLogger('Products.DateRecurringIndex.index')

_marker = object()

VIEW_PERMISSION = 'View'
MGMT_PERMISSION = 'Manage ZCatalogIndex Entries'

manage_addDRIndexForm = DTMLFile('www/addDRIndex', globals())

def manage_addDRIndex(self, id, extra=None, REQUEST=None, RESPONSE=None,
                         URL3=None):
    """Adds a date recurring index"""
    result = self.manage_addIndex(id, 'DateRecurringIndex', extra=extra,
                                  REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
    return result


class DateRecurringIndex(UnIndex):
    """
    """
    __implements__ = (getattr(UnIndex,'__implements__',()),)

    meta_type="DateRecurringIndex"
    security = ClassSecurityInfo()
    manage_options= (
        {'label': 'Settings',
         'action': 'manage_main',
        },
        {'label': 'Browse',
         'action': 'manage_browse'
        },
    )
    manage_main = PageTemplateFile('www/manageDRIndex', globals())
    query_options = ['query', 'range']

    def __init__(self, id, ignore_ex=None, call_methods=None,
                 extra=None, caller=None):
        """ Initialize the index
            @ param extra.start:
            @ param extra.recurdef:
            @ param extral.until:
        """
        UnIndex.__init__(self, id, ignore_ex=None, call_methods=None,
                         extra=None, caller=None)
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

        # TODO: why this try clause?
        try:
            start = getattr(obj, self.attr_start)
            if safe_callable(start):
                start = start()
        except AttributeError:
            return status

        until = getattr(obj, self.attr_until, None)
        if safe_callable(until):
            until = until()

        recurdef = getattr(obj, self.attr_recurdef, None)
        if safe_callable(recurdef):
            recurdef = recurdef()

        from dateutil import rrule
        if isinstance(recurdef, rrule.rrule) or isinstance(recurdef, rrule.rruleset):
            recurconf = RecurConfICal(start, recurdef, until, dst=self.dst)
        else:
            # TODO: don't i get an string and have explicitly cast it into int?
            if not isinstance(recurdef, int):
                recurdef = None
            recurconf = RecurConfTimeDelta(start, recurdef, until, dst=self.dst)

        newvalues = IISet(IRecurringIntSequence(recurconf))
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


    security.declareProtected(VIEW_PERMISSION, 'getStartAttribute')
    def getStartAttribute(self):
        return self.start

    security.declareProtected(VIEW_PERMISSION, 'getRecurDefAttribute')
    def getRecurDefAttribute(self):
        return self.recurdef

    security.declareProtected(VIEW_PERMISSION, 'getUntilAttribute')
    def getUntilAttribute(self):
        return self.until

    security.declareProtected(VIEW_PERMISSION, 'getDSTBehaviour')
    def getDSTBehaviour(self):
        return self.dst


InitializeClass( DateRecurringIndex )
