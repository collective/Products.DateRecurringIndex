from AccessControl.class_init import InitializeClass
from App.special_dtml import DTMLFile
from BTrees.IIBTree import difference
from BTrees.IIBTree import IISet
from logging import getLogger
from OFS.PropertyManager import PropertyManager
from plone.event.recurrence import recurrence_sequence_ical
from plone.event.utils import dt2int
from plone.event.utils import pydt
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluginIndexes.interfaces import IDateRangeIndex
from Products.PluginIndexes.unindex import UnIndex
from Products.PluginIndexes.util import safe_callable
from ZODB.POSException import ConflictError
from zope.interface import implementer
from zope.schema import Text


LOG = getLogger("Products.DateRecurringIndex")
_marker = object()


class IDateRecurringIndex(IDateRangeIndex):
    attr_recurdef = Text(
        title="Attribute- or fieldname of recurrence rule definition."
        "RFC2445 compatible string or timedelta."
    )
    attr_until = Text(title="Attribute- or fieldname of until date (optional).")


@implementer(IDateRecurringIndex)
class DateRecurringIndex(UnIndex, PropertyManager):
    """Index for dates with recurrence support."""

    meta_type = "DateRecurringIndex"
    query_options = ("query", "range", "not")

    manage_main = PageTemplateFile("www/manageDRIndex", globals())
    manage_browse = DTMLFile("www/browseIndex", globals())

    # TODO: for that, this has to be a DTMLFile?
    # manage_main._setName('manage_main')
    manage_options = (
        {"label": "Settings", "action": "manage_main"},
        {"label": "Browse", "action": "manage_browse"},
    ) + PropertyManager.manage_options

    def __init__(self, id, ignore_ex=None, call_methods=None, extra=None, caller=None):
        """Initialize the index
        @ param extra.recurdef:
        @ param extral.until:
        """
        UnIndex.__init__(
            self, id, ignore_ex=None, call_methods=None, extra=None, caller=None
        )
        self.attr_recurdef = extra.recurdef
        self.attr_until = extra.until

    def index_object(self, documentId, obj, threshold=None):
        """index an object, normalizing the indexed value to an integer

        o Normalized value has granularity of one minute.

        o Objects which have 'None' as indexed value are *omitted*,
          by design.

        o Repeat by recurdef - a RFC2445 recurrence definition string

        """
        returnStatus = 0

        try:
            date_attr = getattr(obj, self.id)
            if safe_callable(date_attr):
                date_attr = date_attr()
        except AttributeError:
            return returnStatus

        recurdef = getattr(obj, self.attr_recurdef, None)
        if safe_callable(recurdef):
            recurdef = recurdef()

        if not recurdef:
            dates = [pydt(date_attr)]
        else:
            until = getattr(obj, self.getUntilField(), None)
            if safe_callable(until):
                until = until()

            dates = recurrence_sequence_ical(date_attr, recrule=recurdef, until=until)

        newvalues = IISet(map(dt2int, dates))
        oldvalues = self._unindex.get(documentId, _marker)
        if oldvalues is not _marker:
            oldvalues = IISet(oldvalues)

        if (
            oldvalues is not _marker
            and newvalues is not _marker
            and not difference(newvalues, oldvalues)
            and not difference(oldvalues, newvalues)
        ):
            # difference is calculated relative to first argument, so we have
            # to use it twice here
            return returnStatus

        if oldvalues is not _marker:
            for oldvalue in oldvalues:
                self.removeForwardIndexEntry(oldvalue, documentId)
            if newvalues is _marker:
                try:
                    del self._unindex[documentId]
                except ConflictError:
                    raise
                except Exception:
                    LOG.error(
                        "Should not happen: oldvalues was there,"
                        " now it's not, for document with id %s" % documentId
                    )

        if newvalues is not _marker:
            inserted = False
            for value in newvalues:
                self.insertForwardIndexEntry(value, documentId)
                inserted = True
            if inserted:
                # store tuple values in reverse index entries for sorting
                self._unindex[documentId] = tuple(newvalues)
                returnStatus = 1

        if returnStatus > 0:
            self._increment_counter()

        return returnStatus

    def unindex_object(self, documentId):
        """Carefully unindex the object with integer id 'documentId'"""
        values = self._unindex.get(documentId, _marker)
        if values is _marker:
            return None

        for value in values:
            self.removeForwardIndexEntry(value, documentId)

        try:
            del self._unindex[documentId]
        except ConflictError:
            raise
        except Exception:
            LOG.debug(
                "Attempt to unindex nonexistent document" " with id %s" % documentId,
                exc_info=True,
            )

    def _convert(self, value, default=None):
        """Convert record keys/datetimes into int representation."""
        return dt2int(value) or default

    def getSinceField(self):
        """Get the name of the attribute indexed as start date."""
        return None

    def getUntilField(self):
        """Get the name of the attribute indexed as end date."""
        return self.attr_until


manage_addDRIndexForm = DTMLFile("www/addDRIndex", globals())


def manage_addDRIndex(self, id, extra=None, REQUEST=None, RESPONSE=None, URL3=None):
    """Add a DateRecurringIndex"""
    return self.manage_addIndex(
        id,
        "DateRecurringIndex",
        extra=extra,
        REQUEST=REQUEST,
        RESPONSE=RESPONSE,
        URL1=URL3,
    )


InitializeClass(DateRecurringIndex)
