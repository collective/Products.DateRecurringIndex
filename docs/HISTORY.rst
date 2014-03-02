Changelog
=========

2.1 (2014-03-02)
----------------

- Fix the manage template declaration and avoid the deprecation warnings on
  Zope startup.
  [thet]


2.0.1 (2013-04-24)
------------------

- Licence and contributors updates.
  [jensens]


2.0 (2012-10-12)
----------------

- Use tuple to store self._unindex (reverse index) values, instead of an
  IISet, allowing for proper sorting, intended to fix:
  https://github.com/collective/Products.DateRecurringIndex/issues/1
  For proper sorting, existing installations may wish to reindex any
  indexes installed in their catalog using DateRecurringIndex.
  [seanupton]

2.0b3 (2012-03-02)
------------------

- Fixed broken manage template.
  [romanofski]

- Added template to browse index contents.
  [romanofski]

- Repackaging: Fixing MANIFEST.in and adding missing files.
  [thet]

2.0b2 (2012-02-25)
------------------

- Repackaging: Adding a MANIFEST.in file.
  [thet]

2.0b1 (2012-02-24)
------------------

- Refactoring to support recurrence calculations based on icalendar recurrence
  rules via plone.event.
  [thet]


1.0 (2009-04-10)
----------------

- Initial release
  [jensens]
