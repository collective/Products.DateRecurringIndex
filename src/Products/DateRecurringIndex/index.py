#from BTrees.IIBTree import IIBTree
#from BTrees.IOBTree import IOBTree
#from BTrees.Length import Length
from logging import getLogger
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from BTrees.IIBTree import IISet
from BTrees.IIBTree import union, multiunion, intersection, difference
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from plone.event.utils import dt2int, pydt
from plone.event.recurrence import recurrence_sequence_ical
from ZODB.POSException import ConflictError
from zope.interface import implements
from zope.interface import Interface
from zope.schema import Text

from Products.PluginIndexes.common import safe_callable
from Products.PluginIndexes.common.UnIndex import UnIndex
from Products.PluginIndexes.common.util import parseIndexRequest

LOG = getLogger('Products.DateRecurringIndex')
_marker = object()


class IDateRecurringIndex(Interface):
    attr_recurdef = Text(title=u'Attribute- or fieldname of recurrence rule definition. RFC2445 compatible string or timedelta.')
    attr_until = Text(title=u'Attribute- or fieldname of until date (optional).')


class DateRecurringIndex(UnIndex):

    """Index for dates.
    """
    implements(IDateRecurringIndex)

    meta_type = 'DateRecurringIndex'
    query_options = ('query', 'range')

    manage = manage_main = PageTemplateFile('www/manageDRIndex', globals())
    manage_browse = DTMLFile('www/browseIndex', globals())

    # TODO: for that, this has to be a DTMLFile?
    #manage_main._setName( 'manage_main' )
    manage_options = ( { 'label' : 'Settings'
                       , 'action' : 'manage_main'
                       },
                       {'label': 'Browse',
                        'action': 'manage_browse',
                       },
                     )

    #def clear( self ):
    #    """ Complete reset """
    #    self._index = IOBTree()
    #    self._unindex = IIBTree()
    #    self._length = Length()


    def __init__(self, id, ignore_ex=None, call_methods=None,
                 extra=None, caller=None):
        """ Initialize the index
        @ param extra.recurdef:
        @ param extral.until:
        """
        UnIndex.__init__(self, id, ignore_ex=None, call_methods=None,
                         extra=None, caller=None)
        self.attr_recurdef = extra.recurdef
        self.attr_until = extra.until

    def index_object( self, documentId, obj, threshold=None ):
        """index an object, normalizing the indexed value to an integer

           o Normalized value has granularity of one minute.

           o Objects which have 'None' as indexed value are *omitted*,
             by design.

           o Repeat by recurdef - a RFC2445 reccurence definition string

        """
        returnStatus = 0

        try:
            date_attr = getattr( obj, self.id )
            if safe_callable( date_attr ):
                date_attr = date_attr()
        except AttributeError:
            return returnStatus

        recurdef = getattr(obj, self.attr_recurdef, None)
        if safe_callable(recurdef):
            recurdef = recurdef()

        if not recurdef:
            dates = [pydt(date_attr)]
        else:
            until = getattr(obj, self.attr_until, None)
            if safe_callable(until):
                until = until()

            dates = recurrence_sequence_ical(date_attr, recrule=recurdef, until=until)

        newvalues = IISet(map(dt2int, dates))
        oldvalues = self._unindex.get( documentId, _marker )

        if oldvalues is not _marker and newvalues is not _marker\
            and not difference(newvalues, oldvalues)\
            and not difference(oldvalues, newvalues):
            # difference is calculated relative to first argument, so we have to
            # use it twice here
            return returnStatus

        if oldvalues is not _marker:
            for oldvalue in oldvalues:
                self.removeForwardIndexEntry(oldvalue, documentId)
            if newvalues is _marker:
                try:
                    del self._unindex[documentId]
                except ConflictError:
                    raise
                except:
                    LOG.error("Should not happen: oldvalues was there,"
                                 " now it's not, for document with id %s" %
                                   documentId)

        if newvalues is not _marker:
            inserted = False
            for value in newvalues:
                self.insertForwardIndexEntry( value, documentId )
                inserted = True
            if inserted:
                self._unindex[documentId] = IISet(newvalues) # TODO: IISet necessary here?
                returnStatus = 1

        return returnStatus

    def unindex_object(self, documentId):
        """ Carefully unindex the object with integer id 'documentId'"""
        values = self._unindex.get(documentId, _marker)
        if values is _marker:
            return None

        for value in values:
            self.removeForwardIndexEntry(value, documentId)

        try:
            del self._unindex[documentId]
        except ConflictError:
            raise
        except:
            LOG.debug('Attempt to unindex nonexistent document'
                      ' with id %s' % documentId,exc_info=True)

    def _apply_index(self, request, resultset=None):
        """Apply the index to query parameters given in the argument

        Normalize the 'query' arguments into integer values at minute
        precision before querying.
        """
        record = parseIndexRequest(request, self.id, self.query_options)
        if record.keys is None:
            return None

        keys = map(dt2int, map(pydt, record.keys))

        index = self._index
        r = None
        opr = None

        #experimental code for specifing the operator
        operator = record.get( 'operator', self.useOperator )
        if not operator in self.operators :
            raise RuntimeError("operator not valid: %s" % operator)

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
                    if isinstance(set, int):
                        set = IISet((set,))
                    else:
                        # set can't be bigger than resultset
                        set = intersection(set, resultset)
                    r = set_func(r, set)

        if isinstance(r, int):
            r = IISet((r,))

        if r is None:
            return IISet(), (self.id,)
        else:
            return r, (self.id,)


manage_addDRIndexForm = DTMLFile( 'www/addDRIndex', globals() )

def manage_addDRIndex( self, id, extra=None, REQUEST=None, RESPONSE=None,
                       URL3=None):
    """Add a DateRecurringIndex"""
    return self.manage_addIndex(id, 'DateRecurringIndex', extra=extra, \
                    REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)

InitializeClass(DateRecurringIndex)
